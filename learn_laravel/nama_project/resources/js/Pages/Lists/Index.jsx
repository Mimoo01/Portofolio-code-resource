import { usePage, useForm } from "@inertiajs/react";
import React, { useState, useEffect } from "react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";
import "./task.css";

export default function Index() {
    const { lists, flash, auth } = usePage().props;

    const [showModal, setShowModal] = useState(false);
    const [isEditMode, setIsEditMode] = useState(false);
    const [selectedList, setSelectedList] = useState(null);

    // ======================
    // Inertia Form
    // ======================
    const { data, setData, post, put, reset } = useForm({
        title: "",
        description: "",
        user_id: auth.user.id,
    });

    // ======================
    // useEffect: atur form
    // ======================
    useEffect(() => {
        if (!showModal) return;

        if (isEditMode && selectedList) {
            // MODE EDIT
            setData({
                title: selectedList.title,
                description: selectedList.description,
                user_id: selectedList.user_id,
            });
        } else {
            // MODE CREATE
            reset();
        }
    }, [showModal, isEditMode, selectedList]);

    // ======================
    // Modal handlers
    // ======================
    const openCreateModal = () => {
        setIsEditMode(false);
        setSelectedList(null);
        setShowModal(true);
    };

    const openEditModal = (list) => {
        setIsEditMode(true);
        setSelectedList(list);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedList(null);
    };

    // ======================
    // Submit handlers
    // ======================
    const handleCreate = () => {
        post(route("lists.store"), {
            onSuccess: () => closeModal(),
        });
    };

    const handleUpdate = () => {
        put(route("lists.update", selectedList.id), {
            onSuccess: () => closeModal(),
        });
    };

    return (
        <AuthenticatedLayout>
            <div className="page">
                <h1 className="title">My Lists</h1>

                <button onClick={openCreateModal} className="crlist">
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
                                    <h1>{list.title}</h1>
                                    <p className="mt-2">{list.description}</p>

                                    <div className="actions">
                                        <button
                                            className="button1"
                                            onClick={() => openEditModal(list)}
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

            {/* ======================
                MODAL
            ====================== */}
            {showModal && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
                    onClick={closeModal}
                >
                    <div
                        className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="mb-4 text-lg font-semibold">
                            {isEditMode ? "Edit List" : "Create New List"}
                        </h2>

                        <label className="block mb-2">Judul List</label>
                        <input
                            type="text"
                            value={data.title}
                            onChange={(e) => setData("title", e.target.value)}
                            className="w-full rounded border px-3 py-2"
                        />

                        <label className="block mt-4 mb-2">
                            Keterangan List
                        </label>
                        <input
                            type="text"
                            value={data.description}
                            onChange={(e) =>
                                setData("description", e.target.value)
                            }
                            className="w-full rounded border px-3 py-2"
                        />

                        <div className="mt-6 flex justify-end gap-3">
                            <button
                                onClick={closeModal}
                                className="rounded px-4 py-2 text-gray-600 hover:bg-gray-100"
                            >
                                Cancel
                            </button>

                            <button
                                onClick={
                                    isEditMode ? handleUpdate : handleCreate
                                }
                                className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                            >
                                {isEditMode ? "Update" : "Create"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </AuthenticatedLayout>
    );
}
