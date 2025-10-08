import { useState } from "react";
import { apiPost } from "../api";

interface Props {
  onLogin: (id_pracownika: number) => void;
}

export default function Login({ onLogin }: Props) {
  const [login, setLogin] = useState("");
  const [haslo, setHaslo] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await apiPost("/login", { login, haslo });
      if (res.error) {
        setError(res.error);
        return;
      }
      onLogin(res.id_pracownika);
    } catch {
      setError("Błąd połączenia z serwerem");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-2xl shadow-md w-80"
      >
        <h2 className="text-2xl font-bold text-center mb-6">Logowanie</h2>

        <input
          type="text"
          placeholder="Login (4 litery)"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          className="border rounded px-3 py-2 w-full mb-3"
        />

        <input
          type="password"
          placeholder="Hasło (6 cyfr)"
          value={haslo}
          onChange={(e) => setHaslo(e.target.value)}
          className="border rounded px-3 py-2 w-full mb-3"
        />

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <button
          type="submit"
          className="bg-blue-600 text-white py-2 rounded w-full hover:bg-blue-700"
        >
          Zaloguj
        </button>
      </form>
    </div>
  );
}
