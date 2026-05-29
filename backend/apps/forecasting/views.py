import re

import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge

from apps.scheduling.models import CountingSession, SessionParticipant, Supplier


STORE_NUMBER_RE = re.compile(r"(\d{4})")


def _parse_store_number(people_working: str) -> str:
	if not people_working:
		return ""
	match = STORE_NUMBER_RE.search(people_working)
	return match.group(1) if match else ""


def _build_session_feature(session: CountingSession) -> dict:
	supplier_name = session.supplier.name
	feature = {
		"supplier": supplier_name,
		"store_number": _parse_store_number(session.people_working),
	}

	participant_names = {
		participant.name.strip().lower()
		for participant in session.participants.all()
		if participant.name and participant.name.strip()
	}
	for name in participant_names:
		feature[f"person_{name}_{supplier_name.lower()}"] = 1

	return feature


def _build_request_feature(supplier_name: str, store_number: str, people: list[str]) -> dict:
	feature = {
		"supplier": supplier_name,
		"store_number": store_number,
	}
	for person in {name.strip().lower() for name in people if isinstance(name, str) and name.strip()}:
		feature[f"person_{person}_{supplier_name.lower()}"] = 1
	return feature


def _confidence_for_sessions(count: int) -> str:
	if count < 20:
		return "low"
	if count < 50:
		return "medium"
	return "high"


@api_view(["POST"])
def predict_duration(request):
	supplier_id = request.data.get("supplier_id")
	store_number = str(request.data.get("store_number", "")).strip()
	people = request.data.get("people") or []

	if not supplier_id:
		return Response({"detail": "supplier_id is required."}, status=400)
	if not re.fullmatch(r"\d{4}", store_number):
		return Response({"detail": "store_number must be 4 digits."}, status=400)
	if not isinstance(people, list):
		return Response({"detail": "people must be an array of names."}, status=400)

	try:
		supplier = Supplier.objects.get(pk=supplier_id)
	except Supplier.DoesNotExist:
		return Response({"detail": "Supplier not found."}, status=404)

	completed_sessions = list(
		CountingSession.objects.select_related("supplier")
		.prefetch_related("participants")
		.filter(start_time__isnull=False, end_time__isnull=False, duration_minutes__gt=0)
	)

	sessions_used = len(completed_sessions)
	confidence = _confidence_for_sessions(sessions_used)
	if sessions_used < 2:
		return Response(
			{
				"predicted_minutes": None,
				"range_low": None,
				"range_high": None,
				"confidence": confidence,
				"sessions_used": sessions_used,
				"message": "Not enough completed sessions to train forecast. At least 2 sessions are required.",
			}
		)

	session_features = [_build_session_feature(session) for session in completed_sessions]
	durations = np.array([float(session.duration_minutes) for session in completed_sessions], dtype=float)
	supplier_durations = {}
	for session in completed_sessions:
		supplier_durations.setdefault(session.supplier.name, []).append(float(session.duration_minutes))
	supplier_avg_duration = {
		supplier_name: float(np.mean(values))
		for supplier_name, values in supplier_durations.items()
	}
	overall_avg_duration = float(np.mean(durations))
	y = np.array(
		[
			float(session.duration_minutes) - supplier_avg_duration.get(session.supplier.name, overall_avg_duration)
			for session in completed_sessions
		],
		dtype=float,
	)

	vectorizer = DictVectorizer(sparse=False)
	X = vectorizer.fit_transform(session_features)

	model = Ridge(alpha=10.0)
	model.fit(X, y)

	input_features = _build_request_feature(supplier.name, store_number, people)
	model_adjustment = float(model.predict(vectorizer.transform([input_features]))[0])
	supplier_average = supplier_avg_duration.get(supplier.name, overall_avg_duration)
	predicted = supplier_average + model_adjustment
	predicted = max(predicted, 0.0)

	fitted = model.predict(X)
	residuals = y - fitted
	feature_count = X.shape[1]
	dof = sessions_used - feature_count
	if dof > 0:
		standard_error = float(np.sqrt(np.sum(residuals**2) / dof))
	else:
		standard_error = float(np.std(residuals, ddof=1)) if sessions_used > 1 else 0.0
	if not np.isfinite(standard_error):
		standard_error = 0.0

	range_low = max(predicted - (2 * standard_error), 0.0)
	range_high = max(predicted + (2 * standard_error), 0.0)

	if confidence == "low":
		message = f"Low confidence — only {sessions_used} sessions available"
	elif confidence == "medium":
		message = f"Medium confidence — {sessions_used} sessions used"
	else:
		message = f"High confidence — {sessions_used} sessions used"

	return Response(
		{
			"predicted_minutes": round(predicted, 1),
			"range_low": int(round(range_low)),
			"range_high": int(round(range_high)),
			"confidence": confidence,
			"sessions_used": sessions_used,
			"message": message,
		}
	)


@api_view(["GET"])
def people_list(request):
	names = {
		name.strip()
		for name in SessionParticipant.objects.values_list("name", flat=True)
		if name and name.strip()
	}
	return Response(sorted(names, key=str.lower))


@api_view(["GET"])
def suppliers_list(request):
	suppliers = Supplier.objects.all().order_by("name").values("id", "name")
	return Response(list(suppliers))
