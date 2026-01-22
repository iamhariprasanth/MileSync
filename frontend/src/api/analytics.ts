/**
 * Analytics API client for Opik evaluation and observability metrics.
 */

import { api } from './client';

// Types for analytics responses
export interface EvaluationMetrics {
    opik_enabled: boolean;
    project_name: string | null;
    workspace: string | null;
    recent_evaluations: Record<string, unknown>[];
    summary: Record<string, unknown>;
}

export interface CoachingQualityResult {
    score: number;
    reason: string;
    smart_alignment?: number;
    motivational_quality?: number;
    actionability?: number;
    clarity?: number;
}

export interface FrustrationCheckResult {
    frustration_score: number;
    indicators: string[];
    recommendation: string;
}

export interface AIPerformanceSummary {
    total_conversations: number;
    avg_coaching_quality: number;
    avg_goal_extraction_quality: number;
    avg_frustration_level: number;
    total_goals_created: number;
    model_version: string;
    evaluation_period: string;
}

export interface CoachingMetrics {
    metrics: {
        smart_alignment: {
            specific: number;
            measurable: number;
            achievable: number;
            relevant: number;
            time_bound: number;
        };
        coaching_effectiveness: {
            motivational_quality: number;
            actionability: number;
            clarity: number;
            empathy: number;
        };
        user_engagement: {
            avg_session_length: number;
            goal_completion_rate: number;
            return_user_rate: number;
        };
    };
    period: string;
    model: string;
}

// API functions
export async function getAnalyticsStatus(): Promise<EvaluationMetrics> {
    const response = await api.get('/api/analytics/status');
    return response.data;
}

export async function evaluateCoachingResponse(
    userInput: string,
    aiResponse: string
): Promise<CoachingQualityResult> {
    const response = await api.post('/api/analytics/evaluate/coaching', {
        user_input: userInput,
        ai_response: aiResponse,
    });
    return response.data;
}

export async function checkUserFrustration(
    previousAiResponse: string,
    currentUserReply: string,
    originalUserInput: string
): Promise<FrustrationCheckResult> {
    const response = await api.post('/api/analytics/evaluate/frustration', {
        previous_ai_response: previousAiResponse,
        current_user_reply: currentUserReply,
        original_user_input: originalUserInput,
    });
    return response.data;
}

export async function getAIPerformanceSummary(): Promise<AIPerformanceSummary> {
    const response = await api.get('/api/analytics/performance');
    return response.data;
}

export async function getCoachingMetrics(): Promise<CoachingMetrics> {
    const response = await api.get('/api/analytics/metrics/coaching-quality');
    return response.data;
}

export async function getRecentTraces(limit: number = 10) {
    const response = await api.get('/api/analytics/traces/recent', {
        params: { limit },
    });
    return response.data;
}

