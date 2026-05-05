/* global React, Chip, Button, Icon */

function CreatorCard({ creator, score, reason, onView, onOutreach }) {
  const { display_name, bio, niches = [], city, country, total_followers, avg_engagement_rate, handles = {} } = creator;
  return (
    <div className="sk-creator-card">
      <div className="sk-creator-grid">
        <div>
          <h3 className="sk-creator-name">{display_name || '—'}</h3>
          {bio && <p className="sk-creator-bio">{bio}</p>}
          {niches.length > 0 && (
            <div className="sk-creator-chips">
              {niches.map((n) => <Chip key={n}>{n}</Chip>)}
            </div>
          )}
          {(city || country) && (
            <div className="sk-creator-loc">
              <Icon name="map-pin" size={13} /> {[city, country].filter(Boolean).join(', ')}
            </div>
          )}
        </div>
        <div className="sk-creator-metrics">
          <div>
            <div className="sk-metric">{total_followers ? total_followers.toLocaleString() : '—'}</div>
            <div className="sk-metric-label">Total followers</div>
          </div>
          <div>
            <div className="sk-metric">{((avg_engagement_rate || 0) * 100).toFixed(2)}%</div>
            <div className="sk-metric-label">Engagement</div>
          </div>
        </div>
        <div className="sk-creator-score">
          <div className="sk-score-num">{score?.toFixed(2)}</div>
          <div className="sk-score-label">Match score</div>
          <div className="sk-creator-handles">
            {handles.instagram && <a href="#">IG</a>}
            {handles.tiktok && <a href="#">TikTok</a>}
            {handles.youtube && <a href="#">YouTube</a>}
          </div>
        </div>
      </div>
      {reason && (
        <div className="sk-creator-reason">
          <b>Why this match:</b> {reason}
        </div>
      )}
      <div className="sk-creator-actions">
        <Button variant="outline" size="sm" icon="contact" onClick={onView}>View contact</Button>
        <Button variant="outline" size="sm" icon="mail" onClick={onOutreach}>Draft outreach</Button>
        <Button variant="ghost" size="sm">Open full profile</Button>
      </div>
    </div>
  );
}

Object.assign(window, { CreatorCard });
