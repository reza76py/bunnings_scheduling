import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export default function App() {
  const [suppliers, setSuppliers] = useState([]);
  const [supplierName, setSupplierName] = useState("");
  const [storeNumber, setStoreNumber] = useState("");
  const [value, setValue] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [personInput, setPersonInput] = useState("");
  const [pendingPeople, setPendingPeople] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [startTime, setStartTime] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const loadSuppliers = async () => {
      try {
        const response = await api.get("/api/suppliers/");
        const data = response.data;
        setSuppliers(Array.isArray(data) ? data : data.results || []);
      } catch {
        setErrorMessage("Unable to load suppliers right now.");
      }
    };

    loadSuppliers();
  }, []);

  const isStarted = Boolean(startTime);
  const buttonLabel = isStarted ? "END" : "START";
  const buttonClassName = isStarted
    ? "primary-button end"
    : "primary-button start";
  const cleanPeople = useMemo(() => {
    if (!isStarted) {
      return pendingPeople.map((name) => name.trim()).filter(Boolean);
    }

    return participants
      .filter((participant) => !participant.left_at)
      .map((participant) => participant.name.trim())
      .filter(Boolean);
  }, [isStarted, pendingPeople, participants]);

  const displayParticipants = useMemo(() => {
    if (!isStarted) {
      return [];
    }

    const latestByName = new Map();
    participants.forEach((participant) => {
      const key = participant.name.trim().toLowerCase();
      latestByName.set(key, participant);
    });

    return Array.from(latestByName.values());
  }, [isStarted, participants]);

  const addPerson = async () => {
    const nextPerson = personInput.trim();
    if (!nextPerson) {
      return;
    }

    if (!isStarted) {
      setErrorMessage("");
      setPendingPeople((current) => [...current, nextPerson]);
      setPersonInput("");
      return;
    }

    if (!sessionId) {
      setErrorMessage("Session not found. Please press START first.");
      return;
    }

    try {
      setErrorMessage("");
      const response = await api.post("/api/participants/", {
        session: sessionId,
        name: nextPerson,
        joined_at: new Date().toISOString(),
      });
      setParticipants((current) => [...current, response.data]);
      setPersonInput("");
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.message ||
          "Unable to add participant.",
      );
    }
  };

  const leaveParticipant = async (participantId) => {
    try {
      setErrorMessage("");
      const response = await api.patch(
        `/api/participants/${participantId}/leave/`,
      );
      const updated = response.data;
      setParticipants((current) =>
        current.map((participant) =>
          participant.id === updated.id ? updated : participant,
        ),
      );
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.message ||
          "Unable to leave participant.",
      );
    }
  };

  const rejoinParticipant = async (participantId) => {
    try {
      setErrorMessage("");
      const response = await api.patch(
        `/api/participants/${participantId}/rejoin/`,
      );
      const rejoined = response.data;
      setParticipants((current) => [...current, rejoined]);
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.message ||
          "Unable to rejoin participant.",
      );
    }
  };

  const ensureSupplierId = async () => {
    const typedName = supplierName.trim();

    if (!typedName) {
      throw new Error("Please choose a supplier.");
    }

    const existingSupplier = suppliers.find(
      (supplier) =>
        supplier.name &&
        supplier.name.trim().toLowerCase() === typedName.toLowerCase(),
    );

    if (existingSupplier) {
      setSupplierName(existingSupplier.name);
      return existingSupplier.id;
    }

    const response = await api.post("/api/suppliers/", { name: typedName });
    const createdSupplier = response.data;
    setSuppliers((current) => [...current, createdSupplier]);
    setSupplierName(createdSupplier.name || typedName);
    return createdSupplier.id;
  };

  const resetForm = () => {
    setStoreNumber("");
    setSupplierName("");
    setValue("");
    setSessionId(null);
    setPersonInput("");
    setPendingPeople([]);
    setParticipants([]);
    setStartTime("");
  };

  const handleCancelSession = async () => {
    if (!sessionId || !isStarted) {
      return;
    }

    const confirmed = window.confirm(
      "Cancel this session? This permanently deletes it.",
    );
    if (!confirmed) {
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      await api.delete(`/api/sessions/${sessionId}/`);
      resetForm();
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.message ||
          "Unable to cancel session.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    window.location.reload();
  };

  const handlePrimaryAction = async () => {
    if (!isStarted) {
      setIsSubmitting(true);
      setSuccessMessage("");
      setErrorMessage("");

      try {
        if (!storeNumber.trim()) {
          throw new Error("Please enter a store number.");
        }

        if (!value) {
          throw new Error("Please enter a value.");
        }

        const supplierId = await ensureSupplierId();
        const startedAt = new Date().toISOString();
        const finalPeople = personInput.trim()
          ? [...cleanPeople, personInput.trim()]
          : cleanPeople;

        const response = await api.post("/api/sessions/start/", {
          supplier: supplierId,
          value,
          people_working: `Store ${storeNumber.trim()} | ${finalPeople.join(", ")}`,
        });

        const createdSessionId = response.data.session_id;
        if (pendingPeople.length) {
          const participantResponses = await Promise.all(
            pendingPeople.map((name) =>
              api.post("/api/participants/", {
                session: createdSessionId,
                name,
                joined_at: startedAt,
              }),
            ),
          );
          setParticipants(participantResponses.map((item) => item.data));
        } else {
          setParticipants([]);
        }

        setPendingPeople([]);
        setSessionId(createdSessionId);
        setStartTime(startedAt);
      } catch (error) {
        setErrorMessage(
          error?.response?.data?.detail ||
            error?.message ||
            "Unable to save supplier.",
        );
      } finally {
        setIsSubmitting(false);
      }

      return;
    }

    setIsSubmitting(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      if (!storeNumber.trim()) {
        throw new Error("Please enter a store number.");
      }

      if (!value) {
        throw new Error("Please enter a value.");
      }

      const finalPeople = personInput.trim()
        ? [...cleanPeople, personInput.trim()]
        : cleanPeople;
      if (!finalPeople.length) {
        throw new Error("Please add at least one person working.");
      }

      const supplierId = await ensureSupplierId();
      const endTime = new Date().toISOString();
      if (!sessionId) {
        throw new Error("Session not found. Please press START first.");
      }

      await api.post("/api/sessions/", {
        session_id: sessionId,
        supplier: supplierId,
        value,
        people_working: `Store ${storeNumber.trim()} | ${finalPeople.join(", ")}`,
        start_time: startTime,
        end_time: endTime,
      });

      const durationMs = Math.max(
        0,
        new Date(endTime).getTime() - new Date(startTime).getTime(),
      );
      const totalSeconds = Math.floor(durationMs / 1000);
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;

      setSuccessMessage(
        `✓ Done! Total time: ${minutes} minutes ${seconds} seconds`,
      );
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.message ||
          "Unable to save session.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="session-card">
        <h3>Hi! Simply record when you start and finish the counting.</h3>

        <div className="form-grid">
          <label className="field">
            <input
              type="text"
              value={storeNumber}
              onChange={(event) => setStoreNumber(event.target.value)}
              placeholder="Type store number"
            />
          </label>

          <label className="field">
            <input
              type="text"
              list="supplier-options"
              value={supplierName}
              onChange={(event) => setSupplierName(event.target.value)}
              placeholder="Type or select supplier"
            />
            <datalist id="supplier-options">
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.name} />
              ))}
            </datalist>
          </label>

          <label className="field">
            <input
              type="number"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Enter value ($)"
              inputMode="decimal"
            />
          </label>

          <div className="field">
            <div className="people-list">
              <div className="person-row">
                <input
                  type="text"
                  value={personInput}
                  onChange={(event) => setPersonInput(event.target.value)}
                  placeholder="Who are working on ..."
                />
                <button
                  className="icon-button add"
                  type="button"
                  onClick={addPerson}
                  aria-label="Add person"
                >
                  +
                </button>
              </div>
              {!isStarted
                ? pendingPeople.map((name, index) => (
                    <div className="person-row" key={`pending-person-${index}`}>
                      <input type="text" value={name} readOnly />
                    </div>
                  ))
                : displayParticipants.map((participant) => (
                    <div
                      className="person-row"
                      key={`participant-${participant.id}`}
                    >
                      <input type="text" value={participant.name} readOnly />
                      <button
                        className="icon-button remove"
                        type="button"
                        onClick={() =>
                          participant.left_at
                            ? rejoinParticipant(participant.id)
                            : leaveParticipant(participant.id)
                        }
                        aria-label={
                          participant.left_at ? "Rejoin person" : "Leave person"
                        }
                        style={{
                          width: "52px",
                          minHeight: "52px",
                          borderRadius: "12px",
                          fontSize: "0.6rem",
                          lineHeight: 1,
                          overflow: "hidden",
                          padding: 0,
                          color: "#ffffff",
                          backgroundColor: participant.left_at
                            ? "#e05252"
                            : "#4caf7d",
                          borderColor: participant.left_at
                            ? "#d14b4b"
                            : "#3f9f6f",
                        }}
                      >
                        {participant.left_at ? "✗" : "✓"}
                      </button>
                    </div>
                  ))}
            </div>
          </div>
        </div>

        <div className="action-row">
          <button
            className={buttonClassName}
            type="button"
            onClick={handlePrimaryAction}
            disabled={isSubmitting}
          >
            {isSubmitting ? "SAVING..." : buttonLabel}
          </button>
          {isStarted ? (
            <button
              className="secondary-button cancel"
              type="button"
              onClick={handleCancelSession}
              disabled={isSubmitting}
            >
              CANCEL SESSION
            </button>
          ) : null}
        </div>

        {isStarted ? (
          <p className="time-note">
            Started at {new Date(startTime).toLocaleTimeString()}
          </p>
        ) : null}

        {successMessage ? (
          <>
            <div className="alert success done-box">{successMessage}</div>
            <button
              className="secondary-button"
              type="button"
              onClick={handleNext}
            >
              NEXT
            </button>
          </>
        ) : null}
        {errorMessage ? (
          <div className="alert error">{errorMessage}</div>
        ) : null}
      </section>
    </main>
  );
}
