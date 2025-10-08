import { useState } from "react";
import api from "../api";

export default function Login({ onLogin }: { onLogin: (id: number) => void }) {
  const [login, setLogin] = useState("");
  const [haslo, setHaslo] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      const res = await api.post("/login", { login, haslo });
      if (res.data.id_pracownika) onLogin(res.data.id_pracownika);
      else setError(res.data.error || "Błąd logowania");
    } catch {
      setError("Błąd połączenia z serwerem");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
      <h1 className="text-2xl font-bold mb-6">ProdApp Login</h1>
      <input
        type="text"
        placeholder="Login (4 litery)"
        className="border p-2 rounded mb-2 w-64"
        value={login}
        onChange={(e) => setLogin(e.target.value)}
      />
      <input
        type="password"
        placeholder="Hasło (6 cyfr)"
        className="border p-2 rounded mb-2 w-64"
        value={haslo}
        onChange={(e) => setHaslo(e.target.value)}
      />
      <button
        onClick={handleLogin}
        className="bg-blue-600 text-white px-4 py-2 rounded w-64"
      >
        Zaloguj
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
