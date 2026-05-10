export const BASE_URL = (process.env.REACT_APP_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export const getToken = () => localStorage.getItem("token");

export const authHeaders = () => ({
  Authorization: `Bearer ${getToken()}`,
});

export const formBody = (data) => new URLSearchParams(data).toString();
