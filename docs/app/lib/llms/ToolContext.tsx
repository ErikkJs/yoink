import * as React from "react";
import { DEFAULT_TOOL, type Tool } from "./tools";
import { useLocalStorage } from "./useLocalStorage";

interface ToolContextValue {
  tool: Tool;
  setTool: (tool: Tool) => void;
  hydrated: boolean;
}

const ToolContext = React.createContext<ToolContextValue | null>(null);

const STORAGE_KEY = "yoink.llms.tool";

export function ToolProvider({ children }: { children: React.ReactNode }) {
  const [tool, setTool, hydrated] = useLocalStorage<Tool>(
    STORAGE_KEY,
    DEFAULT_TOOL,
  );

  const value = React.useMemo<ToolContextValue>(
    () => ({ tool, setTool, hydrated }),
    [tool, setTool, hydrated],
  );

  return <ToolContext.Provider value={value}>{children}</ToolContext.Provider>;
}

export function useTool(): ToolContextValue {
  const ctx = React.useContext(ToolContext);
  if (!ctx) {
    throw new Error("useTool must be used inside <ToolProvider>");
  }
  return ctx;
}
