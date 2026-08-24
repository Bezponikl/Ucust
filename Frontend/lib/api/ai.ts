/**
 * AI Service Client & WebSocket Streamer
 * Connects Frontend directly or via Gateway to UnifiedOrchestrator
 */

import { apiClient, AI_GATEWAY_URL, AI_WS_URL } from "./client";

export interface AITaskPayload {
  prompt?: string;
  topic?: string;
  city?: string;
  company_name?: string;
  niche?: string;
  tone?: string;
  format?: "post" | "video" | "photo";
  aspect_ratio?: "1:1" | "4:5" | "16:9" | "9:16";
  generate_image?: boolean;
  [key: string]: unknown;
}

export interface AITaskRequest {
  user_id?: string;
  session_id?: string;
  task_type: "generate_post" | "generate_image" | "prepare_holiday_greeting" | "get_trends" | "rag_query" | string;
  payload: AITaskPayload;
}

export interface AITaskResultData {
  post_text: string;
  promo_code?: string | null;
  video_prompt?: string;
  photo_prompt?: string;
  image_url?: string;
  photo_url?: string;
  confidence_score: number;
  task_type?: string;
  session_id?: string;
  user_id?: string;
}

export interface ImageGenerateRequest {
  prompt: string;
  niche?: string;
  aspect_ratio?: "1:1" | "4:5" | "16:9" | "9:16";
  style?: string;
  brand_colors?: string[];
}

export interface ImageGenerateResponse {
  status: "success" | "error";
  photo_id?: string;
  image_url: string;
  positive_prompt?: string;
  negative_prompt?: string;
  aspect_ratio?: string;
}

export interface AITaskResponse {
  status: "success" | "error";
  data: AITaskResultData;
}

export interface AITrendItem {
  id: number;
  topic: string;
  growth: string;
  volume: string;
}

export interface AITrendsResponse {
  status: string;
  niche: string;
  trends: AITrendItem[];
}

export interface AIAnalyticsResponse {
  status: string;
  reach: number[];
  engagement: number[];
  clicks: number[];
}

export interface AIStreamEvent {
  step: "connected" | "interviewer" | "analyst" | "copywriter" | "completed" | "error";
  progress?: number;
  status?: string;
  message?: string;
  session_id?: string;
  result?: AITaskResultData;
}

/**
 * 1. Synchronous Unified Task Endpoint
 * POST /api/v1/ai/task
 */
export async function submitAiTask(request: AITaskRequest): Promise<AITaskResponse> {
  const userId = request.user_id || "guest_user";
  const sessionId = request.session_id || `sess_${Date.now()}`;

  return apiClient<AITaskResponse>(
    "/api/v1/ai/task",
    {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        session_id: sessionId,
        task_type: request.task_type,
        payload: request.payload,
      }),
    },
    AI_GATEWAY_URL
  );
}

/**
 * 2. Get Niche Trends
 * GET /api/v1/ai/trends?niche=...
 */
export async function fetchAiTrends(niche: string = "SMM"): Promise<AITrendsResponse> {
  return apiClient<AITrendsResponse>(
    "/api/v1/ai/trends",
    {
      params: { niche },
    },
    AI_GATEWAY_URL
  );
}

/**
 * 3. Get AI Analytics Graphs
 * GET /api/v1/ai/analytics/graphs
 */
export async function fetchAiAnalyticsGraphs(): Promise<AIAnalyticsResponse> {
  return apiClient<AIAnalyticsResponse>(
    "/api/v1/ai/analytics/graphs",
    {},
    AI_GATEWAY_URL
  );
}

/**
 * 4. Generate SMM Commercial Image
 * POST /api/v1/ai/generate-image
 */
export async function generateAiImage(params: ImageGenerateRequest): Promise<ImageGenerateResponse> {
  return apiClient<ImageGenerateResponse>(
    "/api/v1/ai/generate-image",
    {
      method: "POST",
      body: JSON.stringify(params),
    },
    AI_GATEWAY_URL
  );
}

/**
 * 5. WebSocket Streaming for Live Agent Steps
 * WS /ws/ai/session/{session_id}
 */
export function connectAiSessionWs(
  sessionId: string,
  callbacks: {
    onEvent: (event: AIStreamEvent) => void;
    onError?: (error: Event) => void;
    onClose?: () => void;
  }
): {
  send: (message: Record<string, unknown>) => void;
  close: () => void;
} {
  const wsUrl = `${AI_WS_URL.replace(/\/+$/, "")}/ws/ai/session/${encodeURIComponent(sessionId)}`;
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as AIStreamEvent;
      callbacks.onEvent(data);
    } catch {
      callbacks.onEvent({
        step: "error",
        message: String(event.data),
      });
    }
  };

  if (callbacks.onError) {
    ws.onerror = callbacks.onError;
  }

  if (callbacks.onClose) {
    ws.onclose = callbacks.onClose;
  }

  return {
    send: (message: Record<string, unknown>) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      } else {
        ws.addEventListener(
          "open",
          () => {
            ws.send(JSON.stringify(message));
          },
          { once: true }
        );
      }
    },
    close: () => {
      ws.close();
    },
  };
}
