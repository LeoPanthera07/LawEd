"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold text-amber-600">NyayaSetu</span>
          <span className="hidden text-xs text-muted-foreground sm:inline">
            Legal Intelligence for Every Citizen
          </span>
        </Link>

        <nav className="flex items-center gap-4">
          {isAuthenticated && user ? (
            <>
              {user.role === "citizen" && (
                <Link
                  href="/dashboard"
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  My Cases
                </Link>
              )}
              {user.role === "lawyer" && (
                <Link
                  href="/lawyer"
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  Review Queue
                </Link>
              )}
              {user.role === "admin" && (
                <Link
                  href="/admin"
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  Admin
                </Link>
              )}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    {user.full_name}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem disabled>
                    {user.email}
                  </DropdownMenuItem>
                  <DropdownMenuItem disabled className="text-xs text-muted-foreground">
                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout}>
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="bg-amber-600 hover:bg-amber-700">
                  Sign up
                </Button>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
