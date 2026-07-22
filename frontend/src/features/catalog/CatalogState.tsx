interface LoadingStateProps {
  message: string;
}

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export function LoadingState({ message }: LoadingStateProps) {
  return (
    <div className="catalog-state" role="status">
      <span aria-hidden="true" className="loading-spinner" />
      <p>{message}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="catalog-state catalog-error" role="alert">
      <p>{message}</p>
      <button className="secondary-button" onClick={onRetry} type="button">
        Reintentar
      </button>
    </div>
  );
}
