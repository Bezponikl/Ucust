import { notFound } from "next/navigation";
import PageWindow from "@/components/dashboard/PageWindow";
import PostEditView from "@/components/dashboard/content/PostEditView";
import { POSTS } from "@/lib/dashboard/content";

export function generateStaticParams() {
  return POSTS.map((p) => ({ id: p.id }));
}

export default async function PostEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const post = POSTS.find((p) => p.id === id);
  if (!post) notFound();

  return (
    <PageWindow>
      <PostEditView post={post} />
    </PageWindow>
  );
}
