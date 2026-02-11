import { usePage, useForm } from "@inertiajs/react";
import React, { useState, useEffect } from "react";
import AuthenticatedLayout from "@/Layouts/AuthenticatedLayout";

export default function Index() {
    const { tasks, flash, auth } = usePage().props;

    return (
        <AuthenticatedLayout>
            <div className="py-12">
                <h1>My Tasks</h1>
                <button onClick={() => console.log("Create new task", tasks)}>
                    Create New Task
                </button>
                <div className="container">
                    {flash?.success && (
                        <div className="alert success">{flash.success}</div>
                    )}
                    {flash?.error && (
                        <div className="alert error">{flash.error}</div>
                    )}
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
