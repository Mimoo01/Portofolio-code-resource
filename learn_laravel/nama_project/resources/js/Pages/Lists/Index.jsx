import React from "react";

export default function Dashboard({ lists }) {
    // Kalau lists belum dikirim dari backend, pakai dummy
    const dummyLists = lists || [
        {
            id: 1,
            name: "Personal Tasks",
            tasks: [
                { id: 1, title: "Belajar Laravel", completed: false },
                { id: 2, title: "Bikin project React", completed: true },
            ],
        },
        {
            id: 2,
            name: "Work Tasks",
            tasks: [
                { id: 3, title: "Kirim laporan", completed: false },
                { id: 4, title: "Meeting jam 10", completed: true },
            ],
        },
    ];

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

            {dummyLists.map((list) => (
                <div
                    key={list.id}
                    className="bg-white shadow rounded-lg p-4 mb-4"
                >
                    <h2 className="text-xl font-semibold mb-2">{list.name}</h2>
                    <ul className="list-disc pl-5">
                        {list.tasks.map((task) => (
                            <li
                                key={task.id}
                                className={
                                    task.completed
                                        ? "line-through text-gray-400"
                                        : ""
                                }
                            >
                                {task.title}
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
}
