import PageWindow from "@/components/dashboard/PageWindow";
import PostEditView from "@/components/dashboard/content/PostEditView";
import RemotePostEditView from "@/components/dashboard/content/RemotePostEditView";
import { POSTS } from "@/lib/dashboard/content";

export function generateStaticParams() {
  return POSTS.map((p) => ({ id: p.id }));
}

export default async function PostEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const post = POSTS.find((p) => p.id === id);

  return (
    <PageWindow>
      {/* Незнакомый id — это пост с бэка: его грузит клиент по /orchestration/posts/{id} */}
      {post ? <PostEditView post={post} /> : <RemotePostEditView id={id} />}
    </PageWindow>
  );
}
