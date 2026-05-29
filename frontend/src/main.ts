import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import Forecast from "./Forecast.jsx";
import "./style.css";

const path = window.location.pathname.replace(/\/$/, "") || "/";
const Page = path === "/forecast" ? Forecast : App;

ReactDOM.createRoot(document.getElementById("app")!).render(
  React.createElement(React.StrictMode, null, React.createElement(Page)),
);
