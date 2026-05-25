"use client";

import { createContext, useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "../../lib/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      setUser({ authenticated: true });
    }
    setIsAuthLoading(false);
  }, []);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);

    const response = await axios.post(
      `${API_BASE_URL}/auth/token`,
      params,
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      },
    );

    axios.defaults.headers.common["Authorization"] =
      `Bearer ${response.data.access_token}`;
    localStorage.setItem("token", response.data.access_token);
    setUser({ username, ...response.data });
    router.push("/");
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
