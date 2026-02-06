import { usePage } from "@inertiajs/react";
import React from "react";
import "./task.css";

export default function Index() {
    const { lists, flash } = usePage().props;

    return (
        <div className="page">
            <div className="container">
                <h1 className="title">My Task Lists</h1>

                {flash?.success && (
                    <div className="alert success">{flash.success}</div>
                )}
                {flash?.error && (
                    <div className="alert error">{flash.error}</div>
                )}

                <ul className="list-wrapper">
                    {lists.length > 0 ? (
                        lists.map((list) => (
                            <li key={list.id} className="list-card">
                                <h3 className="list-title">{list.title}</h3>

                                <ul className="task-wrapper">
                                    {list.tasks.length > 0 ? (
                                        list.tasks.map((task) => (
                                            <li
                                                key={task.id}
                                                className="task-item"
                                            >
                                                {task.title}
                                            </li>
                                        ))
                                    ) : (
                                        <li className="task-empty">No tasks</li>
                                    )}
                                </ul>
                                <button className="button1">Edit</button>
                                <button className="button2">Delete</button>
                            </li>
                        ))
                    ) : (
                        <p className="empty">No task lists available</p>
                    )}
                </ul>
            </div>
        </div>
    );
}
