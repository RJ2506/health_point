import React, {useEffect, useState} from "react";
import "../App.css";

export default function HealthCheck() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [health, setStats] = useState({});
  const [error, setError] = useState(null);

  const getHealth = () => {
    fetch(`http://acit3855-kafka-lab6a.eastus.cloudapp.azure.com:8120/health`)
      .then(res => res.json())
      .then(
        result => {
          console.log("Received Health Points");
          setStats(result);
          setIsLoaded(true);
        },
        error => {
          setError(error);
          setIsLoaded(true);
        }
      )
  };
  useEffect(() => {
    const interval = setInterval(() => getHealth(), 20000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [getHealth]);

  if (error) {
    return <div className={"error"}>Error found when fetching from API</div>;
  } else if (isLoaded === false) {
    return <div>Loading...</div>;
  } else if (isLoaded === true) {
    const date = new Date(health["last_updated"]);
    const seconds = Math.floor(date.getTime() / 1000);
    return (
      <div>
        <h1>Health Points</h1>
        <table className={"StatsTable"}>
          <tbody>
            <tr>
              <th>BUY</th>
              <th>SEARCH</th>
            </tr>
            <tr>
              <td> Receiver: {health["receiver"]}</td>
              <td> Storage: {health["storage"]}</td>
              <td> Processing: {health["max_buy_reading"]}</td>
              <td> Audit: {health["max_search_reading"]}</td>
              <td>Last Updated: {seconds} seconds ago</td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }
}
