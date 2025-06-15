'use client';

import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { ROUTES } from '@/app/_lib/routes';

export default function ExamSelect() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setLoading(true);

        const formData = new FormData(e.currentTarget);
        const payload = {
            subject: formData.get("subject"),
            topic: formData.get("topic"),
            num_questions: Number(formData.get("num_questions")),
            marks_each: Number(formData.get("marks_each")),
            exam_duration: Number(formData.get("exam_duration")),
            deadline_choice: formData.get("deadline_choice"),
            comments: formData.get("comments"),
        };

        try {
            const res = await fetch(ROUTES.API.GENERATE_EXAM, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const questions = await res.json();

            router.push(`/exam/center?data=${encodeURIComponent(JSON.stringify(questions))}`);
        } catch (error) {
            alert("Error generating exam");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Create Exam</h2>
            <form className="space-y-6" onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                    <input
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        type="text"
                        id="subject"
                        name="subject"
                        placeholder="e.g., Math"
                        required
                    />
                </div>

                <div>
                    <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">Topic</label>
                    <input
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        type="text"
                        id="topic"
                        name="topic"
                        placeholder="e.g., Calculus"
                        required
                    />
                </div>

                <div>
                    <label htmlFor="num_questions" className="block text-sm font-medium text-gray-700 mb-1">Number of Questions</label>
                    <input
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        type="number"
                        step="1"
                        min="1"
                        id="num_questions"
                        name="num_questions"
                        defaultValue={5}
                    />
                </div>

                <div>
                    <label htmlFor="marks_each" className="block text-sm font-medium text-gray-700 mb-1">Marks Per Question</label>
                    <input
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        type="number"
                        min="0"
                        id="marks_each"
                        name="marks_each"
                        defaultValue={10}
                    />
                </div>

                <div>
                    <label htmlFor="exam_duration" className="block text-sm font-medium text-gray-700 mb-1">Duration (Minutes)</label>
                    <input
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        type="number"
                        min="0"
                        step="1"
                        id="exam_duration"
                        name="exam_duration"
                        defaultValue={30}
                    />
                </div>

                <div>
                    <label htmlFor="deadline_choice" className="block text-sm font-medium text-gray-700 mb-1">Deadline Choice</label>
                    <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 bg-white text-gray-800"
                        id="deadline_choice"
                        name="deadline_choice"
                        defaultValue="soft_deadline"
                    >
                        <option value="hard_deadline">Hard Deadline — No submissions after time expires</option>
                        <option value="soft_deadline">Soft Deadline — Late submissions with penalty</option>
                        <option value="no_deadline">No Deadline — Submissions allowed anytime</option>
                    </select>
                </div>

                <div>
                    <label htmlFor="comments" className="block text-sm font-medium text-gray-700 mb-1">Comments</label>
                    <textarea
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 text-gray-800 placeholder-gray-500"
                        id="comments"
                        name="comments"
                        placeholder="Comments about the structure or difficulty of the exam"
                        rows={4}
                    ></textarea>
                </div>

                <div className="text-center">
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-md shadow-md hover:bg-blue-700 transition duration-200"
                    >
                        {loading ? "Generating..." : "Create Exam"}
                    </button>
                </div>
            </form>
        </div>
    );
}

