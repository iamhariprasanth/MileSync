import { useState, useEffect } from 'react';
import * as agentsApi from '../../api/agents';

interface HabitTrackerProps {
    goalId?: number;
    compact?: boolean;
}

interface HabitLoop {
    cue: string;
    routine: string;
    reward: string;
}

interface HabitData {
    habit_score: number;
    days_consistent: number;
    habit_loops: HabitLoop[];
}

export default function HabitTracker({ goalId, compact = false }: HabitTrackerProps) {
    const [habitData, setHabitData] = useState<HabitData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadHabitData();
    }, [goalId]);

    async function loadHabitData() {
        setIsLoading(true);
        try {
            const insights = await agentsApi.getInsights(goalId);
            setHabitData(insights.habit_analysis);
        } catch (err) {
            console.error('Failed to load habit data:', err);
        } finally {
            setIsLoading(false);
        }
    }

    if (isLoading) {
        return (
            <div className="animate-pulse bg-gray-100 rounded-lg p-4 h-24"></div>
        );
    }

    if (!habitData) {
        return null;
    }

    if (compact) {
        return (
            <div className="bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg p-4 text-white">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="text-sm opacity-90">Habit Strength</div>
                        <div className="text-2xl font-bold">{habitData.habit_score}/100</div>
                    </div>
                    <div className="text-right">
                        <div className="text-sm opacity-90">Streak</div>
                        <div className="text-2xl font-bold">🔥 {habitData.days_consistent}</div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🔄</span>
                Habit Tracker
            </h3>

            {/* Habit Score Visualization */}
            <div className="flex items-center justify-center mb-6">
                <div className="relative w-24 h-24">
                    <svg className="w-full h-full transform -rotate-90">
                        <circle
                            cx="48" cy="48" r="42"
                            stroke="#f3f4f6" strokeWidth="8" fill="none"
                        />
                        <circle
                            cx="48" cy="48" r="42"
                            stroke="#f97316" strokeWidth="8" fill="none"
                            strokeDasharray={`${(habitData.habit_score / 100) * 264} 264`}
                            strokeLinecap="round"
                            className="transition-all duration-500"
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-2xl font-bold text-gray-900">{habitData.habit_score}</span>
                        <span className="text-xs text-gray-500">score</span>
                    </div>
                </div>
                <div className="ml-6">
                    <div className="text-3xl font-bold text-orange-500">
                        🔥 {habitData.days_consistent}
                    </div>
                    <div className="text-sm text-gray-600">days consistent</div>
                </div>
            </div>

            {/* Habit Loops */}
            {habitData.habit_loops.length > 0 && (
                <div className="space-y-3">
                    <h4 className="font-medium text-gray-700 text-sm">Your Habit Loops</h4>
                    {habitData.habit_loops.map((loop, i) => (
                        <div key={i} className="bg-orange-50 rounded-lg p-3">
                            <div className="flex items-center text-sm">
                                <span className="flex items-center justify-center w-6 h-6 bg-orange-200 rounded-full mr-2 text-xs">
                                    {i + 1}
                                </span>
                                <span className="font-medium text-gray-900">{loop.routine}</span>
                            </div>
                            <div className="mt-2 pl-8 text-xs text-gray-600">
                                <div className="flex items-center">
                                    <span className="w-12 font-medium">Cue:</span>
                                    <span>{loop.cue}</span>
                                </div>
                                <div className="flex items-center mt-1">
                                    <span className="w-12 font-medium">Reward:</span>
                                    <span>{loop.reward}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {habitData.habit_loops.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                    Complete more tasks to build your habit loops!
                </p>
            )}
        </div>
    );
}
