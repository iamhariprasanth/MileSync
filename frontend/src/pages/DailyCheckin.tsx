import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import * as agentsApi from '../api/agents';
import * as goalsApi from '../api/goals';

interface GoalItem {
    id: number;
    title: string;
}

export default function DailyCheckin() {
    const [goals, setGoals] = useState<GoalItem[]>([]);
    const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null);
    const [notes, setNotes] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [checkinResult, setCheckinResult] = useState<any>(null);
    const [dailySummary, setDailySummary] = useState<any>(null);

    useEffect(() => {
        loadGoals();
    }, []);

    useEffect(() => {
        if (selectedGoalId) {
            loadDailySummary(selectedGoalId);
        }
    }, [selectedGoalId]);

    async function loadGoals() {
        setIsLoading(true);
        try {
            const data = await goalsApi.listGoals();
            setGoals(data);
            if (data.length > 0) {
                setSelectedGoalId(data[0].id);
            }
        } catch (err) {
            console.error('Failed to load goals:', err);
        } finally {
            setIsLoading(false);
        }
    }

    async function loadDailySummary(goalId: number) {
        try {
            const summary = await agentsApi.getDailyTasks(goalId);
            setDailySummary(summary);
        } catch (err) {
            console.error('Failed to load daily summary:', err);
        }
    }

    async function handleCheckin() {
        if (!selectedGoalId) return;

        setIsSubmitting(true);
        try {
            const result = await agentsApi.dailyCheckin(selectedGoalId, [], notes);
            setCheckinResult(result);
        } catch (err) {
            console.error('Check-in failed:', err);
        } finally {
            setIsSubmitting(false);
        }
    }

    if (isLoading) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="flex items-center justify-center py-16">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Daily Check-in</h1>
                <p className="mt-2 text-gray-600">
                    Track your progress and get personalized insights
                </p>
            </div>

            {goals.length === 0 ? (
                <div className="bg-white rounded-xl shadow-sm p-8 text-center">
                    <div className="text-6xl mb-4">🎯</div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">No Active Goals</h2>
                    <p className="text-gray-600 mb-4">Start a conversation to create your first goal!</p>
                    <Link
                        to="/chat"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Start Chat
                    </Link>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Goal Selector */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Select Goal
                        </label>
                        <select
                            value={selectedGoalId || ''}
                            onChange={(e) => setSelectedGoalId(Number(e.target.value))}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                            {goals.map((goal) => (
                                <option key={goal.id} value={goal.id}>
                                    {goal.title}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Daily Summary */}
                    {dailySummary && (
                        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-sm p-6 text-white">
                            <h2 className="text-lg font-semibold mb-4">Today's Progress</h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-white/20 rounded-lg p-4 text-center">
                                    <div className="text-3xl font-bold">{dailySummary.daily_summary?.tasks_completed || 0}</div>
                                    <div className="text-sm opacity-90">Completed</div>
                                </div>
                                <div className="bg-white/20 rounded-lg p-4 text-center">
                                    <div className="text-3xl font-bold">{dailySummary.daily_summary?.tasks_pending || 0}</div>
                                    <div className="text-sm opacity-90">Pending</div>
                                </div>
                                <div className="bg-white/20 rounded-lg p-4 text-center">
                                    <div className="text-3xl font-bold">🔥 {dailySummary.daily_summary?.streak_count || 0}</div>
                                    <div className="text-sm opacity-90">Day Streak</div>
                                </div>
                                <div className="bg-white/20 rounded-lg p-4 text-center">
                                    <div className="text-3xl font-bold">{Math.round((dailySummary.daily_summary?.completion_rate || 0) * 100)}%</div>
                                    <div className="text-sm opacity-90">Rate</div>
                                </div>
                            </div>
                            {dailySummary.motivational_message && (
                                <div className="mt-4 p-4 bg-white/10 rounded-lg">
                                    <p className="text-sm">{dailySummary.motivational_message}</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Notes Input */}
                    <div className="bg-white rounded-xl shadow-sm p-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            How are you feeling today? (Optional)
                        </label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Share your thoughts, challenges, or wins..."
                            rows={4}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                        />
                        <button
                            onClick={handleCheckin}
                            disabled={isSubmitting}
                            className="mt-4 w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isSubmitting ? 'Analyzing...' : 'Submit Check-in'}
                        </button>
                    </div>

                    {/* Check-in Results */}
                    {checkinResult && (
                        <div className="space-y-6">
                            {/* Execution Summary */}
                            {checkinResult.execution && (
                                <div className="bg-white rounded-xl shadow-sm p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                        <span className="text-2xl mr-2">📊</span> Execution Summary
                                    </h3>
                                    <div className="prose prose-sm max-w-none text-gray-600">
                                        {checkinResult.execution.motivational_message && (
                                            <p className="bg-blue-50 p-4 rounded-lg">{checkinResult.execution.motivational_message}</p>
                                        )}
                                        {checkinResult.execution.next_actions?.length > 0 && (
                                            <div className="mt-4">
                                                <h4 className="font-medium text-gray-900">Next Actions:</h4>
                                                <ul className="mt-2 space-y-2">
                                                    {checkinResult.execution.next_actions.map((action: string, i: number) => (
                                                        <li key={i} className="flex items-start">
                                                            <span className="text-blue-500 mr-2">→</span>
                                                            {action}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Sustainability Insights */}
                            {checkinResult.sustainability && (
                                <div className="bg-white rounded-xl shadow-sm p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                        <span className="text-2xl mr-2">🌱</span> Sustainability Insights
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div className="bg-gray-50 rounded-lg p-4">
                                            <div className="text-2xl font-bold text-green-600">
                                                {checkinResult.sustainability.sustainability_score || 0}/100
                                            </div>
                                            <div className="text-sm text-gray-600">Sustainability Score</div>
                                        </div>
                                        <div className="bg-gray-50 rounded-lg p-4">
                                            <div className={`text-2xl font-bold ${checkinResult.sustainability.burnout_risk === 'LOW' ? 'text-green-600' :
                                                    checkinResult.sustainability.burnout_risk === 'MEDIUM' ? 'text-yellow-600' : 'text-red-600'
                                                }`}>
                                                {checkinResult.sustainability.burnout_risk || 'LOW'}
                                            </div>
                                            <div className="text-sm text-gray-600">Burnout Risk</div>
                                        </div>
                                    </div>
                                    {checkinResult.sustainability.recommendations?.length > 0 && (
                                        <div className="space-y-2">
                                            <h4 className="font-medium text-gray-900">Recommendations:</h4>
                                            {checkinResult.sustainability.recommendations.map((rec: string, i: number) => (
                                                <div key={i} className="flex items-start bg-green-50 p-3 rounded-lg">
                                                    <span className="text-green-500 mr-2">💡</span>
                                                    <span className="text-sm text-gray-700">{rec}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Psychological Support */}
                            {checkinResult.psychological && (
                                <div className="bg-white rounded-xl shadow-sm p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                        <span className="text-2xl mr-2">💜</span> Mindset Support
                                    </h3>
                                    {checkinResult.psychological.intervention && (
                                        <div className="bg-purple-50 p-4 rounded-lg mb-4">
                                            <h4 className="font-medium text-purple-900 mb-2">
                                                {checkinResult.psychological.intervention.technique}
                                            </h4>
                                            <p className="text-sm text-purple-800 mb-3">
                                                {checkinResult.psychological.intervention.message}
                                            </p>
                                            {checkinResult.psychological.intervention.exercises?.length > 0 && (
                                                <ol className="list-decimal list-inside text-sm text-purple-700 space-y-1">
                                                    {checkinResult.psychological.intervention.exercises.map((ex: string, i: number) => (
                                                        <li key={i}>{ex}</li>
                                                    ))}
                                                </ol>
                                            )}
                                        </div>
                                    )}
                                    {checkinResult.psychological.affirmations?.length > 0 && (
                                        <div className="space-y-2">
                                            {checkinResult.psychological.affirmations.map((aff: string, i: number) => (
                                                <div key={i} className="flex items-center text-sm text-gray-700">
                                                    <span className="mr-2">✨</span>
                                                    {aff}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
