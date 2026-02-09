import { usePage, useForm } from "@inertiajs/react";
import React, { useState } from "react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import "./task.css";

export default function Index() {
    const { lists, flash } = usePage().props;

    const [showModal, setShowModal] = useState(false);
    const [isEditMode, setIsEditMode] = useState(false);
    const [selectedList, setSelectedList] = useState(null);

    // inertia form
    const { data, setData, put, reset } = useForm({
        title: "",
        description: "",
        user_id: usePage().props.auth.user.id,
    });

    // Open Modal & set form data
    const openModal = (list) => {
        setSelectedList(list);
        setData({
            title: list.title,
            description: list.description,
            user_id: list.user_id,
        });
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedList(null);
    };

    const handleSave = () => {
        // put(route("lists.update", [selectedList.id, selectedList.id]), data, {
        //     onSuccess: () => closeModal(),
        // });
        put(route("lists.update", selectedList.id, data), {
            onSuccess: () => {
                closeModal(); // tutup modal kalau sukses
            },
        });
    };

    return (
        <AuthenticatedLayout>
            <div className="page">
                <h1 className="title">My Task Lists</h1>
                <button
                    onClick={() => {
                        setShowModal(true);
                        setIsEditMode(false);
                    }}
                    className="crlist"
                >
                    Create New List
                </button>

                <div className="container">
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
                                            <li className="task-empty">
                                                No tasks
                                            </li>
                                        )}
                                    </ul>

                                    <div className="actions">
                                        <button
                                            className="button1"
                                            onClick={() => {
                                                console.log(
                                                    "Edit di klik",
                                                    list,
                                                );
                                                openModal(list);
                                                setIsEditMode(true);
                                            }}
                                        >
                                            Edit
                                        </button>
                                        <button className="button2">
                                            Delete
                                        </button>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <p className="empty">No task lists available</p>
                        )}
                    </ul>
                </div>
            </div>

            {/* ===== MODAL ===== */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div
                        className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="mb-4 text-lg font-semibold">
                            Edit List
                        </h2>

                        <input
                            type="text"
                            value={data.title}
                            onChange={(e) => setData("title", e.target.value)}
                            className="w-full rounded border px-3 py-2 focus:outline-none focus:ring"
                        />

                        <input
                            type="text"
                            value={data.description}
                            onChange={(e) =>
                                setData("description", e.target.value)
                            }
                            className="mt-4 w-full rounded border px-3 py-2 focus:outline-none focus:ring"
                        />

                        <div className="mt-6 flex justify-end gap-3">
                            <button
                                onClick={closeModal}
                                className="rounded px-4 py-2 text-gray-600 hover:bg-gray-100"
                            >
                                Cancel
                            </button>

                            <button
                                onClick={handleSave}
                                className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                            >
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </AuthenticatedLayout>
    );
}
