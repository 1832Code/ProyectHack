"use client";

export default function ClaimError({ error }: { error: Error }) {
  return <div>Error loading company information: {error.message}</div>;
}