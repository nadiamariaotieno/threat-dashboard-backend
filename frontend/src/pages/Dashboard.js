import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

const Dashboard = () => {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/reports")
      .then((response) => {
        setReports(response.data);
      })
      .catch((error) => {
        console.error("Error fetching reports:", error);
      });
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>Threat Analysis Dashboard</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={reports}>
          <XAxis dataKey="title" tick={{ fontSize: 10 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="sentiment" fill="#82ca9d" />
          <Bar dataKey="threat_level" fill="#ff6666" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Dashboard;
