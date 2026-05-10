function Generator({
  topic,
  result,
  date,
  time,
  onTopicChange,
  onGenerate,
  onDateChange,
  onTimeChange,
  onSchedule,
  onPostNow,
}) {
  return (
    <section className="generator">
      <h2>Generate Content</h2>

      <input type="text" placeholder="Enter topic..." value={topic} onChange={onTopicChange} />
      <button onClick={onGenerate}>Generate</button>

      {result && (
        <div className="result-card">
          <h3>Generated Content</h3>
          <p>{result}</p>

          <h4>Schedule LinkedIn Post</h4>

          <input type="date" value={date} onChange={onDateChange} />
          <input type="time" value={time} onChange={onTimeChange} />

          <div className="schedule-actions">
            <button onClick={onSchedule}>Schedule</button>
            <button onClick={onPostNow}>Post Now</button>
          </div>
        </div>
      )}
    </section>
  );
}

export default Generator;
