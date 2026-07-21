interface PlaceholderPageProps {
  description: string;
  title: string;
}

export function PlaceholderPage({ description, title }: PlaceholderPageProps) {
  return (
    <section className="placeholder-page">
      <p className="eyebrow">Próximamente</p>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}
