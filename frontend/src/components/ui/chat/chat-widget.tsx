"use client";

import { useState } from "react";
import { MessageSquare, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatWindow } from "./chat-window";

export function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="fixed bottom-4 right-4 z-50">
            {isOpen ? (
                <div className="relative">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-background"
                        onClick={() => setIsOpen(false)}
                    >
                        <X className="h-4 w-4" />
                    </Button>
                    <ChatWindow />
                </div>
            ) : (
                <Button
                    variant="default"
                    size="icon"
                    className="h-12 w-12 rounded-full shadow-lg"
                    onClick={() => setIsOpen(true)}
                >
                    <MessageSquare className="h-6 w-6" />
                </Button>
            )}
        </div>
    );
} 