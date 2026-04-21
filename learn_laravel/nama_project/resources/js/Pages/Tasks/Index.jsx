import { usePage, useForm } from "@inertiajs/react";
import React, { useState, useEffect } from "react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";

export default function Index() {
    const { tasks, flash, auth } = usePage().props;

    const { showModal, setShowModal } = useState(false);
    const { isEditMode, setIsEditMode } = useState(false);
    const { selectedList, setSelectedList } = useState(null);

    const { data, setData, post, put, reset } = useForm({
        title: "",
        description: "",
        user_id: auth.user.id,
    });

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

    const handleCreate = () => {
        post(route("tasks.store"), {
            onSuccess: () => closeModal(),
        });
    };

    const handleUpdate = () => {
        put(route("tasks.update", selectedList.id), {
            onSuccess: () => closeModal(),
        });
    };

    return (
        <AuthenticatedLayout>
            <div className="page">
                <h1 className="title">My Tasks</h1>
                <button
                    onClick={() => console.log("Create new task", tasks)}
                    className="crlist"
                >
                    Create New Task
                </button>
                <select
                    value={tasks.list_id}
                    className="crlist"
                    onChange={(e) => {
                        console.log("Selected list:", e.target.value);
                    }}
                >
                    {tasks.map((task) => (
                        <option key={task.id} value={task.list_id}>
                            {task.list?.title || "No List"}
                        </option>
                    ))}
                </select>

                <div className="container">
                    {flash?.success && (
                        <div className="alert success">{flash.success}</div>
                    )}
                    {flash?.error && (
                        <div className="alert error">{flash.error}</div>
                    )}

                    <ul className="list-wrapper">
                        {tasks.length > 0 ? (
                            tasks.map((task) => (
                                <li key={task.id} className="list-card">
                                    <h1>{task.title}</h1>
                                    <p className="mt-2">{task.description}</p>

                                    <div className="actions">
                                        <button
                                            className="button1"
                                            onClick={() => {
                                                console.log(list);
                                                openEditModal(list);
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
        </AuthenticatedLayout>
    );
}
