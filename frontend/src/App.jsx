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
  const [people, setPeople] = useState([""]);
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
  const cleanPeople = useMemo(
    () => people.map((person) => person.trim()).filter(Boolean),
    [people],
  );

  const updatePerson = (index, nextValue) => {
    setPeople((current) =>
      current.map((person, i) => (i === index ? nextValue : person)),
    );
  };

  const addPersonRow = () => {
    setPeople((current) => [...current, ""]);
  };

  const removePersonRow = (index) => {
    setPeople((current) => {
      if (current.length === 1) {
        return current;
      }

      return current.filter((_, i) => i !== index);
    });
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
    setPeople([""]);
    setStartTime("");
  };

  const handlePrimaryAction = async () => {
    if (!isStarted) {
      setIsSubmitting(true);
      setSuccessMessage("");
      setErrorMessage("");

      try {
        await ensureSupplierId();
        setStartTime(new Date().toISOString());
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

      if (!cleanPeople.length) {
        throw new Error("Please add at least one person working.");
      }

      const supplierId = await ensureSupplierId();
      const endTime = new Date().toISOString();

      await api.post("/api/sessions/", {
        supplier: supplierId,
        value,
        people_working: `Store ${storeNumber.trim()} | ${cleanPeople.join(", ")}`,
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
      resetForm();
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
        <h1>Counting</h1>

        <div className="form-grid">
          <label className="field">
            <span>Store Number</span>
            <input
              type="text"
              value={storeNumber}
              onChange={(event) => setStoreNumber(event.target.value)}
              placeholder="Type store number"
            />
          </label>

          <label className="field">
            <span>Supplier Name</span>
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
            <span>Value</span>
            <input
              type="number"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Enter value"
              inputMode="decimal"
            />
          </label>

          <div className="field">
            <span>People Working</span>
            <div className="people-list">
              {people.map((person, index) => (
                <div className="person-row" key={`person-${index}`}>
                  <input
                    type="text"
                    value={person}
                    onChange={(event) =>
                      updatePerson(index, event.target.value)
                    }
                    placeholder={
                      index === 0 ? "First person" : `Person ${index + 1}`
                    }
                  />
                  {index === 0 ? (
                    <button
                      className="icon-button add"
                      type="button"
                      onClick={addPersonRow}
                      aria-label="Add person"
                    >
                      +
                    </button>
                  ) : (
                    <button
                      className="icon-button remove"
                      type="button"
                      onClick={() => removePersonRow(index)}
                      aria-label="Remove person"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <button
          className={buttonClassName}
          type="button"
          onClick={handlePrimaryAction}
          disabled={isSubmitting}
        >
          {isSubmitting ? "SAVING..." : buttonLabel}
        </button>

        {isStarted ? (
          <p className="time-note">
            Started at {new Date(startTime).toLocaleTimeString()}
          </p>
        ) : null}

        {successMessage ? (
          <div className="alert success done-box">{successMessage}</div>
        ) : null}
        {errorMessage ? (
          <div className="alert error">{errorMessage}</div>
        ) : null}
      </section>
    </main>
  );
}
