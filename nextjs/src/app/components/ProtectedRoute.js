"use client";

import { useContext, useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthContext from "../context/AuthContext";

const ProtectedRoute = ({ children }) => {
    const { user, isAuthLoading } = useContext(AuthContext);
    const router = useRouter();

    useEffect(() => {
        if (isAuthLoading) {
            return;
        }
        if (!user) {
            router.push("/login");
        }
    }, [user, isAuthLoading, router]);

    if (isAuthLoading) {
        return null;
    }

    return user ? children : null;
};

export default ProtectedRoute;
