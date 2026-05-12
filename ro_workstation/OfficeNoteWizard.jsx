import { useState, useRef } from "react";

const STEPS = ["Reference Info", "Branch Details", "Transaction", "Policy Reference", "Review & Confirm"];

const initialForm = {
  refNo: "RO/PLNG/2025/06/01",
  date: new Date().toLocaleDateString("en-GB").replace(/\//g, "."),
  noteType: "HIGH VALUE DEMAND DRAFT",
  branchSOLID: "",
  gradeOfHead: "",
  applicantName: "",
  accountNumber: "",
  kycCompliance: "Yes",
  dateOfIssue: "",
  beneficiaryName: "",
  amount: "",
  issuingBranch: "",
  ddDrawnOn: "",
  purpose: "",
  transactionId: "",
  policies: [
    { department: "Inter Branch Reconciliation Division", date: "02.04.2011", circularRef: "1/2011-12" },
    { department: "Banking Operations", date: "01.11.2018", circularRef: "Misc/452/2018-19" },
  ],
  recommendation: "Since the branch request satisfies extant guidelines in the referred circulars, we may approve the entry in Finacle using HHVDD menu.",
};

function StepIndicator({ current }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 0, marginBottom: "2rem" }}>
      {STEPS.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", flex: i < STEPS.length - 1 ? 1 : "none" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <div style={{
                width: 32, height: 32, borderRadius: "50%",
                background: done ? "#1a3a6b" : active ? "#1a3a6b" : "var(--color-background-secondary)",
                border: active ? "2px solid #1a3a6b" : done ? "2px solid #1a3a6b" : "1.5px solid var(--color-border-secondary)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 500,
                color: done || active ? "#fff" : "var(--color-text-secondary)",
                transition: "all 0.2s",
                flexShrink: 0,
              }}>
                {done ? <i className="ti ti-check" style={{ fontSize: 14 }} aria-hidden="true" /> : i + 1}
              </div>
              <span style={{
                fontSize: 11, fontWeight: active ? 500 : 400,
                color: active ? "#1a3a6b" : done ? "var(--color-text-secondary)" : "var(--color-text-tertiary)",
                whiteSpace: "nowrap", textAlign: "center", maxWidth: 72,
                lineHeight: 1.3,
              }}>{label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{
                flex: 1, height: 1.5, marginBottom: 22,
                background: done ? "#1a3a6b" : "var(--color-border-tertiary)",
                transition: "background 0.2s",
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}

function Field({ label, required, children }) {
  return (
    <div style={{ marginBottom: "1.1rem" }}>
      <label style={{ display: "block", fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {label}{required && <span style={{ color: "#c0392b", marginLeft: 3 }}>*</span>}
      </label>
      {children}
    </div>
  );
}

function Input({ value, onChange, placeholder, type = "text" }) {
  return (
    <input type={type} value={value} onChange={onChange} placeholder={placeholder}
      style={{ width: "100%", boxSizing: "border-box", fontSize: 14 }} />
  );
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={onChange} style={{ width: "100%", fontSize: 14 }}>
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

function TwoCol({ children }) {
  return <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 1.5rem" }}>{children}</div>;
}

function SectionHead({ icon, title }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: "1.25rem", paddingBottom: "0.6rem", borderBottom: "1.5px solid #1a3a6b22" }}>
      <i className={`ti ti-${icon}`} style={{ fontSize: 18, color: "#1a3a6b" }} aria-hidden="true" />
      <span style={{ fontSize: 15, fontWeight: 500, color: "#1a3a6b" }}>{title}</span>
    </div>
  );
}

function PreviewTable({ data }) {
  const rows = [
    ["Branch SOL ID", data.branchSOLID],
    ["Grade of Branch head", data.gradeOfHead],
    ["Name of the applicant", data.applicantName],
    ["Account number", data.accountNumber],
    ["Compliance of KYC norms", data.kycCompliance],
    ["Date of Issue", data.dateOfIssue],
    ["Name of Beneficiary", data.beneficiaryName],
    ["Amount of Draft to be issued", data.amount ? `₹ ${Number(data.amount.replace(/,/g, "")).toLocaleString("en-IN")}.00/-` : ""],
    ["Issuing Branch", data.issuingBranch],
    ["DD Drawn on", data.ddDrawnOn],
    ["Purpose of transaction", data.purpose],
    ["Transaction ID", data.transactionId],
  ];
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
      <thead>
        <tr style={{ background: "#1a3a6b", color: "#fff" }}>
          <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500, width: "45%" }}>Particulars</th>
          <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500 }}>Branch Reply</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([k, v], i) => (
          <tr key={k} style={{ background: i % 2 === 0 ? "var(--color-background-primary)" : "var(--color-background-secondary)" }}>
            <td style={{ padding: "7px 12px", fontWeight: 500, borderBottom: "0.5px solid var(--color-border-tertiary)", fontSize: 12 }}>{k}</td>
            <td style={{ padding: "7px 12px", borderBottom: "0.5px solid var(--color-border-tertiary)", color: "var(--color-text-primary)" }}>{v || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PolicyTable({ policies }) {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
      <thead>
        <tr style={{ background: "#1a3a6b", color: "#fff" }}>
          <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500 }}>Issuing Department</th>
          <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500, width: 110 }}>Date</th>
          <th style={{ padding: "8px 12px", textAlign: "left", fontWeight: 500, width: 140 }}>Circular Ref No</th>
        </tr>
      </thead>
      <tbody>
        {policies.map((p, i) => (
          <tr key={i} style={{ background: i % 2 === 0 ? "var(--color-background-primary)" : "var(--color-background-secondary)" }}>
            <td style={{ padding: "7px 12px", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>{p.department || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}</td>
            <td style={{ padding: "7px 12px", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>{p.date || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}</td>
            <td style={{ padding: "7px 12px", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>{p.circularRef || <span style={{ color: "var(--color-text-tertiary)" }}>—</span>}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function App() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(initialForm);
  const [submitted, setSubmitted] = useState(false);
  const previewRef = useRef(null);

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }));
  const setPolicy = (i, key) => (e) => {
    const updated = form.policies.map((p, idx) => idx === i ? { ...p, [key]: e.target.value } : p);
    setForm(f => ({ ...f, policies: updated }));
  };
  const addPolicy = () => setForm(f => ({ ...f, policies: [...f.policies, { department: "", date: "", circularRef: "" }] }));
  const removePolicy = (i) => setForm(f => ({ ...f, policies: f.policies.filter((_, idx) => idx !== i) }));

  const next = () => setStep(s => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep(s => Math.max(s - 1, 0));

  const gradeOptions = [
    { value: "", label: "Select grade…" },
    { value: "MM I", label: "MM I" }, { value: "MM II", label: "MM II" },
    { value: "MM III", label: "MM III" }, { value: "SM I", label: "SM I" },
    { value: "SM II", label: "SM II" }, { value: "SM III", label: "SM III" },
    { value: "TEG IV", label: "TEG IV" }, { value: "TEG V", label: "TEG V" },
    { value: "TEG VI", label: "TEG VI" }, { value: "TEG VII", label: "TEG VII" },
  ];

  const handleSubmit = () => setSubmitted(true);
  const handleReset = () => { setForm(initialForm); setStep(0); setSubmitted(false); };

  if (submitted) {
    return (
      <div style={{ padding: "2rem 0" }}>
        <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: "1.5rem" }}>
            <div style={{ width: 36, height: 36, borderRadius: "50%", background: "#1a3a6b", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <i className="ti ti-check" style={{ fontSize: 18, color: "#fff" }} />
            </div>
            <div>
              <div style={{ fontWeight: 500, fontSize: 15, color: "var(--color-text-primary)" }}>Office note generated</div>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>Ref: {form.refNo} · {form.date}</div>
            </div>
          </div>

          <div ref={previewRef} style={{ border: "0.5px solid var(--color-border-secondary)", borderRadius: "var(--border-radius-md)", overflow: "hidden", marginBottom: "1.25rem" }}>
            <div style={{ background: "#1a3a6b", padding: "14px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 16, fontWeight: 500, color: "#fff", letterSpacing: "0.02em" }}>Indian Overseas Bank</div>
              <div style={{ fontSize: 11, color: "#cbd5e8", marginTop: 2 }}>Regional Office, Dindigul</div>
            </div>
            <div style={{ padding: "14px 16px", borderBottom: "0.5px solid var(--color-border-tertiary)", display: "flex", justifyContent: "space-between", fontSize: 12 }}>
              <span style={{ color: "var(--color-text-secondary)" }}>Ref No: <strong style={{ color: "var(--color-text-primary)" }}>{form.refNo}</strong></span>
              <span style={{ color: "var(--color-text-secondary)" }}>Date: <strong style={{ color: "var(--color-text-primary)" }}>{form.date}</strong></span>
            </div>
            <div style={{ padding: "10px 16px 6px", textAlign: "center", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)", letterSpacing: "0.04em" }}>OFFICE NOTE</div>
              <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 2 }}>{form.noteType}</div>
              <div style={{ fontSize: 12, fontWeight: 500, color: "#1a3a6b", marginTop: 4 }}>
                {form.issuingBranch} ({form.branchSOLID}) · {form.transactionId} · {form.applicantName}
              </div>
            </div>
            <div style={{ padding: "14px 16px" }}>
              <PreviewTable data={form} />
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: 11, fontWeight: 500, letterSpacing: "0.06em", color: "var(--color-text-secondary)", marginBottom: 8 }}>POLICY REFERENCE</div>
                <PolicyTable policies={form.policies} />
              </div>
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: 11, fontWeight: 500, letterSpacing: "0.06em", color: "var(--color-text-secondary)", marginBottom: 6 }}>DEPARTMENT RECOMMENDATION</div>
                <p style={{ fontSize: 13, color: "var(--color-text-primary)", margin: 0, lineHeight: 1.6 }}>{form.recommendation}</p>
              </div>
            </div>
          </div>

          <button onClick={handleReset} style={{ width: "100%" }}>
            <i className="ti ti-refresh" style={{ marginRight: 6, fontSize: 14 }} aria-hidden="true" />
            Create another office note
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "1.5rem 0" }}>
      <h2 className="sr-only">Office Note Creation Wizard</h2>
      <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", overflow: "hidden" }}>
        <div style={{ background: "#1a3a6b", padding: "16px 20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <i className="ti ti-file-text" style={{ fontSize: 20, color: "#fff" }} aria-hidden="true" />
            <div>
              <div style={{ color: "#fff", fontWeight: 500, fontSize: 15 }}>Office Note Wizard</div>
              <div style={{ color: "#a8bbd8", fontSize: 12 }}>Indian Overseas Bank · Regional Office, Dindigul</div>
            </div>
          </div>
        </div>

        <div style={{ padding: "1.5rem 1.5rem 0" }}>
          <StepIndicator current={step} />
        </div>

        <div style={{ padding: "0 1.5rem 1.5rem" }}>

          {step === 0 && (
            <div>
              <SectionHead icon="id" title="Reference information" />
              <TwoCol>
                <Field label="Reference number" required>
                  <Input value={form.refNo} onChange={set("refNo")} placeholder="RO/PLNG/2025/06/01" />
                </Field>
                <Field label="Date" required>
                  <Input value={form.date} onChange={set("date")} placeholder="DD.MM.YYYY" />
                </Field>
              </TwoCol>
              <Field label="Note type / Subject" required>
                <Input value={form.noteType} onChange={set("noteType")} placeholder="e.g. HIGH VALUE DEMAND DRAFT" />
              </Field>
            </div>
          )}

          {step === 1 && (
            <div>
              <SectionHead icon="building-bank" title="Branch details" />
              <TwoCol>
                <Field label="Branch SOL ID" required>
                  <Input value={form.branchSOLID} onChange={set("branchSOLID")} placeholder="e.g. 0332" />
                </Field>
                <Field label="Grade of branch head" required>
                  <Select value={form.gradeOfHead} onChange={set("gradeOfHead")} options={gradeOptions} />
                </Field>
              </TwoCol>
              <TwoCol>
                <Field label="Issuing branch" required>
                  <Input value={form.issuingBranch} onChange={set("issuingBranch")} placeholder="e.g. Dindigul Main (0332)" />
                </Field>
                <Field label="DD drawn on" required>
                  <Input value={form.ddDrawnOn} onChange={set("ddDrawnOn")} placeholder="e.g. Dindigul Main (0332)" />
                </Field>
              </TwoCol>
              <TwoCol>
                <Field label="Applicant name" required>
                  <Input value={form.applicantName} onChange={set("applicantName")} placeholder="Name of applicant" />
                </Field>
                <Field label="Account number" required>
                  <Input value={form.accountNumber} onChange={set("accountNumber")} placeholder="Account number" />
                </Field>
              </TwoCol>
              <Field label="KYC compliance">
                <Select value={form.kycCompliance} onChange={set("kycCompliance")} options={[{ value: "Yes", label: "Yes" }, { value: "No", label: "No" }]} />
              </Field>
            </div>
          )}

          {step === 2 && (
            <div>
              <SectionHead icon="receipt" title="Transaction details" />
              <TwoCol>
                <Field label="Date of issue" required>
                  <Input value={form.dateOfIssue} onChange={set("dateOfIssue")} placeholder="DD.MM.YYYY" />
                </Field>
                <Field label="Transaction ID" required>
                  <Input value={form.transactionId} onChange={set("transactionId")} placeholder="e.g. IB401211" />
                </Field>
              </TwoCol>
              <Field label="Beneficiary name" required>
                <Input value={form.beneficiaryName} onChange={set("beneficiaryName")} placeholder="Name of beneficiary" />
              </Field>
              <TwoCol>
                <Field label="Amount (₹)" required>
                  <Input value={form.amount} onChange={set("amount")} placeholder="e.g. 2869651" />
                </Field>
                <Field label="Purpose of transaction" required>
                  <Input value={form.purpose} onChange={set("purpose")} placeholder="e.g. EB Bill Payment" />
                </Field>
              </TwoCol>
            </div>
          )}

          {step === 3 && (
            <div>
              <SectionHead icon="clipboard-list" title="Policy reference" />
              {form.policies.map((p, i) => (
                <div key={i} style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px", marginBottom: "0.75rem", position: "relative" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                    <span style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)" }}>Policy {i + 1}</span>
                    {form.policies.length > 1 && (
                      <button onClick={() => removePolicy(i)} style={{ fontSize: 12, padding: "2px 8px", color: "var(--color-text-danger)" }}>
                        <i className="ti ti-trash" style={{ fontSize: 13 }} aria-hidden="true" /> Remove
                      </button>
                    )}
                  </div>
                  <Field label="Issuing department">
                    <Input value={p.department} onChange={setPolicy(i, "department")} placeholder="Department name" />
                  </Field>
                  <TwoCol>
                    <Field label="Date">
                      <Input value={p.date} onChange={setPolicy(i, "date")} placeholder="DD.MM.YYYY" />
                    </Field>
                    <Field label="Circular ref no">
                      <Input value={p.circularRef} onChange={setPolicy(i, "circularRef")} placeholder="e.g. 1/2011-12" />
                    </Field>
                  </TwoCol>
                </div>
              ))}
              <button onClick={addPolicy} style={{ width: "100%", marginTop: "0.25rem", fontSize: 13 }}>
                <i className="ti ti-plus" style={{ marginRight: 5, fontSize: 13 }} aria-hidden="true" />
                Add policy row
              </button>

              <div style={{ marginTop: "1.25rem" }}>
                <SectionHead icon="message-dots" title="Department recommendation" />
                <textarea value={form.recommendation} onChange={set("recommendation")}
                  rows={4}
                  style={{ width: "100%", boxSizing: "border-box", fontSize: 14, resize: "vertical", padding: 10, borderRadius: "var(--border-radius-md)", border: "0.5px solid var(--color-border-secondary)", background: "var(--color-background-primary)", color: "var(--color-text-primary)", fontFamily: "var(--font-sans)", lineHeight: 1.6 }}
                />
              </div>
            </div>
          )}

          {step === 4 && (
            <div>
              <SectionHead icon="eye" title="Review" />
              <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "10px 14px", marginBottom: "1rem", fontSize: 12, color: "var(--color-text-secondary)" }}>
                <i className="ti ti-info-circle" style={{ fontSize: 14, marginRight: 5, verticalAlign: -2 }} aria-hidden="true" />
                Preview of the generated office note (letterhead and signatures excluded)
              </div>
              <div style={{ border: "0.5px solid var(--color-border-secondary)", borderRadius: "var(--border-radius-md)", overflow: "hidden" }}>
                <div style={{ background: "#1a3a6b", padding: "12px 16px", textAlign: "center" }}>
                  <div style={{ fontSize: 14, fontWeight: 500, color: "#fff" }}>Indian Overseas Bank · Regional Office, Dindigul</div>
                </div>
                <div style={{ padding: "10px 14px", display: "flex", justifyContent: "space-between", fontSize: 12, borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
                  <span>Ref: <strong>{form.refNo}</strong></span>
                  <span>Date: <strong>{form.date}</strong></span>
                </div>
                <div style={{ padding: "8px 14px 4px", textAlign: "center", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
                  <div style={{ fontWeight: 500, fontSize: 13, color: "var(--color-text-primary)" }}>OFFICE NOTE</div>
                  <div style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{form.noteType}</div>
                  <div style={{ fontSize: 12, fontWeight: 500, color: "#1a3a6b", marginTop: 3 }}>
                    {form.issuingBranch || "—"} · {form.transactionId || "—"} · {form.applicantName || "—"}
                  </div>
                </div>
                <div style={{ padding: "12px 14px" }}>
                  <PreviewTable data={form} />
                  <div style={{ marginTop: "0.75rem" }}>
                    <div style={{ fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", color: "var(--color-text-secondary)", marginBottom: 6 }}>POLICY REFERENCE</div>
                    <PolicyTable policies={form.policies} />
                  </div>
                  <div style={{ marginTop: "0.75rem" }}>
                    <div style={{ fontSize: 10, fontWeight: 500, letterSpacing: "0.06em", color: "var(--color-text-secondary)", marginBottom: 5 }}>DEPARTMENT RECOMMENDATION</div>
                    <p style={{ fontSize: 12, margin: 0, lineHeight: 1.6, color: "var(--color-text-primary)" }}>{form.recommendation}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem", justifyContent: "space-between" }}>
            <button onClick={prev} style={{ opacity: step === 0 ? 0.4 : 1, pointerEvents: step === 0 ? "none" : "auto" }}>
              <i className="ti ti-arrow-left" style={{ marginRight: 5, fontSize: 14 }} aria-hidden="true" />
              Back
            </button>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              {step < STEPS.length - 1 ? (
                <button onClick={next} style={{ background: "#1a3a6b", color: "#fff", border: "none", padding: "8px 20px", borderRadius: "var(--border-radius-md)", cursor: "pointer", fontSize: 14 }}>
                  Continue
                  <i className="ti ti-arrow-right" style={{ marginLeft: 5, fontSize: 14 }} aria-hidden="true" />
                </button>
              ) : (
                <button onClick={handleSubmit} style={{ background: "#1a3a6b", color: "#fff", border: "none", padding: "8px 20px", borderRadius: "var(--border-radius-md)", cursor: "pointer", fontSize: 14 }}>
                  <i className="ti ti-check" style={{ marginRight: 5, fontSize: 14 }} aria-hidden="true" />
                  Generate note
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
