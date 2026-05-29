import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

const confidenceStyleMap = {
  low: { color: "var(--error)", label: "LOW" },
  medium: { color: "#f1c40f", label: "MEDIUM" },
  high: { color: "var(--success)", label: "HIGH" },
};

export default function Forecast() {
  const [suppliers, setSuppliers] = useState([]);
  const [peopleOptions, setPeopleOptions] = useState([]);
  const [supplierId, setSupplierId] = useState("");
  const [storeNumber, setStoreNumber] = useState("");
  const [selectedPeople, setSelectedPeople] = useState({});
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);


  // Load suppliers on mount
  useEffect(() => {
    const loadSuppliers = async () => {
      try {
        const response = await api.get("/api/forecast/suppliers/");
        setSuppliers(Array.isArray(response.data) ? response.data : []);
      } catch {
        setSuppliers([]);
      }
    };
    loadSuppliers();
  }, []);

  // Load people when storeNumber changes
  useEffect(() => {
    const fetchPeople = async () => {
      try {
        let url = "/api/forecast/people/";
        if (/^\d{4}$/.test(storeNumber)) {
          url += `?store=${storeNumber}`;
        }
        const response = await api.get(url);
        setPeopleOptions(Array.isArray(response.data) ? response.data : []);
        setSelectedPeople({}); // Clear selection when store changes
      } catch {
        setPeopleOptions([]);
        setSelectedPeople({});
      }
    };
    fetchPeople();
  }, [storeNumber]);

  const chosenPeople = useMemo(
    () =>
      Object.entries(selectedPeople)
        .filter(([, selected]) => selected)
        .map(([name]) => name),
    [selectedPeople],
  );

  const togglePerson = (name) => {
    setSelectedPeople((current) => ({
      ...current,
      [name]: !current[name],
    }));
  };

  const handleStoreNumberChange = (event) => {
    const digitsOnly = event.target.value.replace(/\D/g, "").slice(0, 4);
    setStoreNumber(digitsOnly);
  };

  const handlePredict = async () => {
    setErrorMessage("");
    setResult(null);

    if (!supplierId) {
      setErrorMessage("Please choose a supplier.");
      return;
    }

    if (!/^\d{4}$/.test(storeNumber)) {
      setErrorMessage("Please enter a valid 4-digit store number.");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post("/api/forecast/predict/", {
        supplier_id: Number(supplierId),
        store_number: storeNumber,
        people: chosenPeople,
      });
      setResult(response.data);
    } catch (error) {
      setErrorMessage(
        error?.response?.data?.detail ||
          error?.response?.data?.message ||
          error?.message ||
          "Unable to predict duration.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const confidenceView =
    confidenceStyleMap[result?.confidence] || confidenceStyleMap.low;

  return (
    <main className="page-shell">
      <section className="session-card">
        <div style={{ marginBottom: "10px" }}>
          <a
            href="/"
            style={{
              color: "var(--secondary)",
              textDecoration: "none",
              fontSize: "0.9rem",
              fontWeight: 700,
            }}
          >
            ← Back to Recording
          </a>
        </div>

        <h3>Forecast expected counting duration.</h3>

        <div className="form-grid">
          <label className="field">
            <span>Supplier</span>
            <select
              value={supplierId}
              onChange={(event) => setSupplierId(event.target.value)}
            >
              <option value="">Select supplier</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Store Number</span>
            <input
              type="text"
              value={storeNumber}
              onChange={handleStoreNumberChange}
              inputMode="numeric"
              maxLength={4}
              placeholder="Type 4-digit store number"
            />
          </label>

          <div className="field">
            <span>People</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(peopleOptions && peopleOptions.length) ? (
                peopleOptions.map((person) => (
                  <label
                    key={person}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      cursor: 'pointer',
                      padding: '8px 12px',
                      borderRadius: '8px',
                      background: selectedPeople[person]
                        ? 'rgba(79, 142, 247, 0.15)'
                        : 'transparent',
                      border: '1px solid',
                      borderColor: selectedPeople[person]
                        ? 'rgba(79, 142, 247, 0.5)'
                        : 'var(--border)',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={!!selectedPeople[person]}
                      onChange={() => togglePerson(person)}
                      style={{
                        width: '20px',
                        height: '20px',
                        cursor: 'pointer',
                        accentColor: 'var(--secondary)',
                        flexShrink: 0,
                      }}
                    />
                    <span style={{
                      color: 'var(--text-main)',
                      fontSize: '0.95rem',
                      fontWeight: '500',
                    }}>
                      {person}
                    </span>
                  </label>
                ))
              ) : (
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  No people found yet.
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="action-row">
          <button
            className="primary-button start"
            type="button"
            onClick={handlePredict}
            disabled={isSubmitting}
          >
            {isSubmitting ? "PREDICTING..." : "PREDICT"}
          </button>
        </div>

        {result ? (
          <div className="alert success" style={{ marginTop: "16px" }}>
            <div
              style={{
                fontSize: "1rem",
                color: "var(--text-main)",
                marginBottom: "6px",
              }}
            >
              Predicted range: {result.range_low ?? "-"} —{" "}
              {result.range_high ?? "-"} minutes
            </div>
            <div style={{ marginBottom: "6px" }}>
              Confidence:{" "}
              <strong style={{ color: confidenceView.color }}>
                {confidenceView.label}
              </strong>
            </div>
            <div style={{ color: "var(--text-main)", marginBottom: "6px" }}>
              Sessions used: {result.sessions_used}
            </div>
            <div style={{ color: "var(--text-muted)" }}>{result.message}</div>
            {result.confidence === "low" ? (
              <div className="alert error" style={{ marginTop: "10px" }}>
                Warning: Low confidence forecast. Add more completed sessions
                for better accuracy.
              </div>
            ) : null}
          </div>
        ) : null}

        {errorMessage ? (
          <div className="alert error">{errorMessage}</div>
        ) : null}
      </section>
    </main>
  );
}
