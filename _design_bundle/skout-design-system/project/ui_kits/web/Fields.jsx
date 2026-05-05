/* global React, Chip, Button, Icon */
const { useState } = React;

function Input({ label, placeholder, value, onChange, required, hint, type = 'text' }) {
  return (
    <div className="sk-field">
      {label && <label className="sk-label-field">{label}{required && ' *'}</label>}
      {type === 'textarea' ? (
        <textarea className="sk-input" placeholder={placeholder} value={value || ''} onChange={(e) => onChange?.(e.target.value)} rows={4} />
      ) : (
        <input className="sk-input" type={type} placeholder={placeholder} value={value || ''} onChange={(e) => onChange?.(e.target.value)} />
      )}
      {hint && <span className="sk-hint">{hint}</span>}
    </div>
  );
}

function ChipSelect({ label, options, value = [], onChange }) {
  const toggle = (o) => {
    const next = value.includes(o) ? value.filter((v) => v !== o) : [...value, o];
    onChange?.(next);
  };
  return (
    <div className="sk-field">
      {label && <label className="sk-label-field">{label}</label>}
      <div className="sk-chipselect">
        {options.map((o) => (
          <button key={o} type="button" onClick={() => toggle(o)} className={`sk-chip-btn ${value.includes(o) ? 'is-on' : ''}`}>{o}</button>
        ))}
      </div>
    </div>
  );
}

function Select({ label, options, value, onChange }) {
  return (
    <div className="sk-field">
      {label && <label className="sk-label-field">{label}</label>}
      <select className="sk-input" value={value || ''} onChange={(e) => onChange?.(e.target.value)}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function NumberField({ label, value, onChange, min, max, step }) {
  return (
    <div className="sk-field">
      {label && <label className="sk-label-field">{label}</label>}
      <input className="sk-input" type="number" value={value ?? ''} min={min} max={max} step={step} onChange={(e) => onChange?.(Number(e.target.value))} />
    </div>
  );
}

function Checkbox({ label, checked, onChange }) {
  return (
    <label className="sk-check">
      <input type="checkbox" checked={!!checked} onChange={(e) => onChange?.(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

Object.assign(window, { Input, ChipSelect, Select, NumberField, Checkbox });
