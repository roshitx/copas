"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
    const { theme, setTheme, resolvedTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    // Prevent hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return (
            <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                aria-label="Toggle theme"
                disabled
            >
                <span className="h-4 w-4" />
            </Button>
        );
    }

    const currentTheme = theme === "system" ? resolvedTheme : theme;

    const toggleTheme = () => {
        if (theme === "light") {
            setTheme("dark");
        } else if (theme === "dark") {
            setTheme("system");
        } else {
            setTheme("light");
        }
    };

    const getIcon = () => {
        switch (theme) {
            case "light":
                return <Sun className="h-4 w-4" />;
            case "dark":
                return <Moon className="h-4 w-4" />;
            case "system":
            default:
                return <Monitor className="h-4 w-4" />;
        }
    };

    const getLabel = () => {
        switch (theme) {
            case "light":
                return "Switch to dark mode";
            case "dark":
                return "Switch to system preference";
            case "system":
            default:
                return "Switch to light mode";
        }
    };

    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="h-9 w-9 text-muted-foreground hover:text-foreground transition-colors"
            aria-label={getLabel()}
            title={`Theme: ${theme} (${currentTheme})`}
        >
            {getIcon()}
        </Button>
    );
}
