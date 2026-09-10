"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import { toMessage } from "@/lib/api/errors";
import { toDashboardPost } from "@/lib/api/mapGeneration";
import { getPost } from "@/lib/api/orchestration";
import type { Post } from "@/lib/dashboard/content";
import PostEditView from "./PostEditView";

/**
 * Пост, которого нет в демо-плане витрины: адрес открыт по id с бэка. Грузим
 * его на клиенте — статически такие страницы не собрать, id появляется только
 * после генерации.
 */
export default function RemotePostEditView({ id }: { id: string }) {
  const [post, setPost] = useState<Post | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void getPost(id)
      .then((data) => {
        if (!cancelled) setPost(toDashboardPost(data));
      })
      .catch((err) => {
        if (!cancelled) setError(toMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (post) return <PostEditView post={post} serverId={id} />;

  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-20 text-center" aria-live="polite">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-surface-soft text-ink-muted">
        <Icon name={error ? "file-text" : "clock"} size={22} aria-hidden="true" />
      </span>
      <p className="text-sm font-medium text-ink">
        {error ? "Публикация не открылась" : "Загружаем публикацию…"}
      </p>
      {error && (
        <>
          <p className="max-w-sm text-sm text-ink-muted">{error}</p>
          <Link
            href="/dashboard/content"
            className="btn-glass mt-2 inline-flex items-center justify-center px-5 py-2.5 text-sm font-semibold"
          >
            К контент-плану
          </Link>
        </>
      )}
    </div>
  );
}
