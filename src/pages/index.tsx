import { useState } from "react";
import reactLogo from "../assets/react.svg";
import viteLogo from "/vite.svg";
import { Button } from "@/components/ui/button";
//import "../App.css";

export default function Home() {
  const [count, setCount] = useState(0);

  return (
    <div className="w-full h-screen flex flex-col items-center justify-center gap-6">
      <div className="w-full flex justify-center gap-4">
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="w-20 logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="w-20 logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="flex flex-col items-center justify-center gap-6">
        <Button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </Button>
        <p>
          Link to{" "}
          <a className="underline" href="/dashboard">
            Dashboard
          </a>
        </p>
      </div>
    </div>
  );
}
