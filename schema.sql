-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Table to store curriculum topics and their embeddings
create table if not exists curriculum_topics (
  id bigint primary key generated always as identity,
  topic_text text not null,
  embedding vector(384), -- Using 384 dimensions for all-MiniLM-L6-v2
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Table to store resources (videos, articles)
create table if not exists resources (
  id bigint primary key generated always as identity,
  url text not null unique,
  title text,
  type text, -- 'youtube', 'article', etc.
  is_processed boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Table to store chunks of text from resources and their embeddings
create table if not exists resource_chunks (
  id bigint primary key generated always as identity,
  resource_id bigint references resources(id) on delete cascade,
  chunk_text text not null,
  embedding vector(384),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create a function to search for curriculum topics
create or replace function match_curriculum_topics (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  topic_text text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    curriculum_topics.id,
    curriculum_topics.topic_text,
    1 - (curriculum_topics.embedding <=> query_embedding) as similarity
  from curriculum_topics
  where 1 - (curriculum_topics.embedding <=> query_embedding) > match_threshold
  order by curriculum_topics.embedding <=> query_embedding
  limit match_count;
end;
$$;