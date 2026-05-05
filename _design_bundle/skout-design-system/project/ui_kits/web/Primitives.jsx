/* global React */
const { useState, useEffect, useRef } = React;

// ============ Icon (Lucide via CDN) ============
function Icon({ name, size = 20, strokeWidth = 1.75, style }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current && window.lucide) {
      ref.current.innerHTML = '';
      const el = document.createElement('i');
      el.setAttribute('data-lucide', name);
      ref.current.appendChild(el);
      window.lucide.createIcons({ attrs: { width: size, height: size, 'stroke-width': strokeWidth } });
    }
  }, [name, size, strokeWidth]);
  return <span ref={ref} style={{ display: 'inline-flex', alignItems: 'center', ...style }} />;
}

// ============ Button ============
function Button({ variant = 'primary', size = 'md', icon, children, onClick, as: Tag = 'button', href, style }) {
  const baseCls = `sk-btn sk-btn-${variant} sk-btn-${size}`;
  const props = Tag === 'a' ? { href, onClick } : { onClick };
  return (
    <Tag className={baseCls} {...props} style={style}>
      {icon && <Icon name={icon} size={size === 'sm' ? 14 : 16} />}
      <span>{children}</span>
    </Tag>
  );
}

// ============ Badge / Eyebrow ============
function Eyebrow({ children, marker = true }) {
  return <span className="sk-eyebrow">{marker && <span className="sk-eyebrow-mark">✦</span>} {children}</span>;
}
function Chip({ children, tone = 'blue' }) {
  return <span className={`sk-chip sk-chip-${tone}`}>{children}</span>;
}
function StatusDot({ online = true, label }) {
  return (
    <span className={online ? 'sk-status sk-online' : 'sk-status sk-offline'}>
      <span className="sk-dot"></span>{label || (online ? 'Backend online' : 'Backend offline')}
    </span>
  );
}

// ============ Logo ============
function Logo({ size = 28 }) {
  return (
    <a href="#home" className="sk-logo" onClick={(e) => { e.preventDefault(); window.__nav?.('home'); }}>
      <img src="../../assets/logo-skout-owl.svg" alt="" width={size} height={size} />
      <span>Skout<span className="sk-logo-dot">.</span></span>
    </a>
  );
}

// ============ Word-by-word reveal ============
function WordReveal({ text, delay = 0, className = '' }) {
  const words = text.split(' ');
  return (
    <span className={className}>
      {words.map((w, i) => (
        <span key={i} className="sk-word" style={{ animationDelay: `${delay + i * 60}ms` }}>
          {w}{i < words.length - 1 ? '\u00A0' : ''}
        </span>
      ))}
    </span>
  );
}

Object.assign(window, { Icon, Button, Eyebrow, Chip, StatusDot, Logo, WordReveal });
