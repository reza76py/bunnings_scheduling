import { useEffect, useState } from "react";
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

const NEW_SUPPLIER_VALUE = "__new__";

export default function App() {
  const [suppliers, setSuppliers] = useState([]);
  const [supplierChoice, setSupplierChoice] = useState("");
  const [newSupplierName, setNewSupplierName] = useState("");
  const [value, setValue] = useState("");
  const [peopleWorking, setPeopleWorking] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
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

  const isAddingNewSupplier = supplierChoice === NEW_SUPPLIER_VALUE;
  const canEndSession = Boolean(startTime) && !isSubmitting;

  const handleStart = () => {
    const now = new Date().toISOString();
    setStartTime(now);
    setEndTime("");
    setSuccessMessage("");
    setErrorMessage("");
  };

  const ensureSupplierId = async () => {
    if (isAddingNewSupplier) {
      const name = newSupplierName.trim();

      if (!name) {
        throw new Error("Please type a supplier name.");
      }

      const response = await api.post("/api/suppliers/", { name });
      const createdSupplier = response.data;
      setSuppliers((currentSuppliers) => [
        ...currentSuppliers,
        createdSupplier,
      ]);
      setSupplierChoice(String(createdSupplier.id));
      setNewSupplierName("");
      return createdSupplier.id;
    }

    if (!supplierChoice) {
      throw new Error("Please choose a supplier.");
    }

    return supplierChoice;
  };

  const handleEnd = async () => {
    if (!startTime) {
      return;
    }

    setIsSubmitting(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      const finishedAt = new Date().toISOString();
      setEndTime(finishedAt);

      const supplierId = await ensureSupplierId();

      await api.post("/api/sessions/", {
        supplier: supplierId,
        value,
        people_working: peopleWorking,
        start_time: startTime,
        end_time: finishedAt,
      });

      setSuccessMessage("Session saved successfully.");
      setValue("");
      setPeopleWorking("");
      setStartTime("");
      setEndTime("");
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
      <section className="card">
        <div className="header-copy">


        </div>

        <div className="form-grid">
          <label className="field">
            <span>Supplier Name</span>
            <select
              value={supplierChoice}
              onChange={(event) => setSupplierChoice(event.target.value)}
            >
              <option value="">Select a supplier</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
              <option value={NEW_SUPPLIER_VALUE}>Add a new supplier...</option>
            </select>
          </label>

          {isAddingNewSupplier ? (
            <label className="field">
              <span>New Supplier Name</span>
              <input
                type="text"
                value={newSupplierName}
                onChange={(event) => setNewSupplierName(event.target.value)}
                placeholder="Type supplier name"
              />
            </label>
          ) : null}

          <label className="field">
            <span>Value</span>
            <input
              type="number"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Enter value"
              inputMode="decimal"
            />
          </label>

          <label className="field">
            <span>People Working</span>
            <input
              type="text"
              value={peopleWorking}
              onChange={(event) => setPeopleWorking(event.target.value)}
              placeholder="Names or crew count"
            />
          </label>
        </div>

        <div className="actions">
          <button
            className="button button-start"
            type="button"
            onClick={handleStart}
            disabled={Boolean(startTime) && !endTime}
          >
            START
          </button>
          <button
            className="button button-end"
            type="button"
            onClick={handleEnd}
            disabled={!canEndSession}
          >
            END
          </button>
        </div>

        <div className="status-row">
          <p>
            <strong>Start:</strong>{" "}
            {startTime
              ? new Date(startTime).toLocaleString()
              : "Not started yet"}
          </p>
          <p>
            <strong>End:</strong>{" "}
            {endTime ? new Date(endTime).toLocaleString() : "Not recorded yet"}
          </p>
        </div>

        {successMessage ? (
          <div className="alert alert-success">{successMessage}</div>
        ) : null}
        {errorMessage ? (
          <div className="alert alert-error">{errorMessage}</div>
        ) : null}
      </section>
    </main>
  );
}
