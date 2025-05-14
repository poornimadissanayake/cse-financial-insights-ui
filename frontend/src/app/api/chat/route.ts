import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
    try {
        const { message } = await req.json();
        console.log("Sending message to backend:", message);

        // Make request to FastAPI backend
        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error("Backend error:", errorData);
            throw new Error(`Backend error: ${response.status} - ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        console.log("Received response from backend:", data);
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error processing chat message:", error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : "Failed to process message" },
            { status: 500 }
        );
    }
} 