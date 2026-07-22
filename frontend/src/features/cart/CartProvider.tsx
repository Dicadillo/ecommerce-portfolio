import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import {
  addCartItem,
  clearCart,
  deleteCartItem,
  getCart,
  updateCartItem,
} from '../../api/cartApi';
import { getProduct } from '../../api/catalogApi';
import { useAuth } from '../../hooks/useAuth';
import type { Cart, CartProducts } from '../../types/cart';
import type { Product } from '../../types/catalog';
import { parseApiError } from '../../utils/apiErrors';
import { CartContext } from './CartContext';

interface CartProviderProps {
  children: ReactNode;
}

interface CartRequestState {
  cart: Cart | null;
  error: string;
  key: string;
  products: CartProducts;
  status: 'idle' | 'loading' | 'ready' | 'error';
}

const anonymousState: CartRequestState = {
  cart: null,
  error: '',
  key: 'anonymous',
  products: {},
  status: 'idle',
};

export function CartProvider({ children }: CartProviderProps) {
  const { isAuthenticated, user } = useAuth();
  const [retryVersion, setRetryVersion] = useState(0);
  const authenticatedUserId = isAuthenticated ? user?.id : undefined;
  const requestKey = authenticatedUserId
    ? `${authenticatedUserId}:${retryVersion}`
    : 'anonymous';
  const [request, setRequest] = useState<CartRequestState>(anonymousState);
  const [isMutating, setIsMutating] = useState(false);
  const productCache = useRef(new Map<number, Product>());

  const loadCart = useCallback(async (key: string, signal?: AbortSignal) => {
    const cart = await getCart(signal);
    const productIds = [...new Set(cart.articulos.map((item) => item.producto))];
    const missingProductIds = productIds.filter(
      (productId) => !productCache.current.has(productId),
    );

    await Promise.all(
      missingProductIds.map(async (productId) => {
        const product = await getProduct(productId, signal);
        productCache.current.set(productId, product);
      }),
    );

    const products = Object.fromEntries(
      productIds.flatMap((productId) => {
        const product = productCache.current.get(productId);
        return product ? [[productId, product]] : [];
      }),
    );

    return { cart, error: '', key, products, status: 'ready' as const };
  }, []);

  useEffect(() => {
    if (!authenticatedUserId) {
      return;
    }

    const controller = new AbortController();

    void loadCart(requestKey, controller.signal)
      .then(setRequest)
      .catch((requestError: unknown) => {
        if (!controller.signal.aborted) {
          setRequest({
            cart: null,
            error: parseApiError(requestError, 'No se pudo cargar el carrito.').message,
            key: requestKey,
            products: {},
            status: 'error',
          });
        }
      });

    return () => controller.abort();
  }, [authenticatedUserId, loadCart, requestKey]);

  const currentRequest = useMemo(
    () =>
      request.key === requestKey
        ? request
        : authenticatedUserId
          ? {
              cart: null,
              error: '',
              key: requestKey,
              products: {},
              status: 'loading' as const,
            }
          : anonymousState,
    [authenticatedUserId, request, requestKey],
  );

  const refreshAfterMutation = useCallback(async () => {
    if (!authenticatedUserId) {
      throw new Error('Debes iniciar sesión para modificar el carrito.');
    }

    const refreshedRequest = await loadCart(requestKey);
    setRequest(refreshedRequest);
  }, [authenticatedUserId, loadCart, requestKey]);

  const runMutation = useCallback(async (mutation: () => Promise<void>) => {
    setIsMutating(true);
    try {
      await mutation();
    } finally {
      setIsMutating(false);
    }
  }, []);

  const addProduct = useCallback(
    async (product: Product, quantity = 1) => {
      if (!product.activo || product.stock < quantity) {
        throw new Error('El producto no está disponible en la cantidad solicitada.');
      }

      productCache.current.set(product.id, product);
      await runMutation(async () => {
        await addCartItem(product.id, quantity);
        await refreshAfterMutation();
      });
    },
    [refreshAfterMutation, runMutation],
  );

  const updateQuantity = useCallback(
    async (itemId: number, quantity: number) => {
      if (quantity < 1) {
        throw new Error('La cantidad no puede ser menor que uno.');
      }

      await runMutation(async () => {
        await updateCartItem(itemId, quantity);
        await refreshAfterMutation();
      });
    },
    [refreshAfterMutation, runMutation],
  );

  const removeItem = useCallback(
    async (itemId: number) => {
      await runMutation(async () => {
        await deleteCartItem(itemId);
        await refreshAfterMutation();
      });
    },
    [refreshAfterMutation, runMutation],
  );

  const clear = useCallback(async () => {
    await runMutation(async () => {
      await clearCart();
      await refreshAfterMutation();
    });
  }, [refreshAfterMutation, runMutation]);

  const completeCheckout = useCallback(() => {
    productCache.current.clear();
    setRequest((current) => ({
      cart:
        current.key === requestKey && current.cart
          ? {
              ...current.cart,
              articulos: [],
              cantidad_total: 0,
              total: '0.00',
            }
          : null,
      error: '',
      key: requestKey,
      products: {},
      status: 'ready',
    }));
  }, [requestKey]);

  const value = useMemo(
    () => ({
      addProduct,
      cart: currentRequest.cart,
      clear,
      completeCheckout,
      error: currentRequest.error,
      isLoading: currentRequest.status === 'loading',
      isMutating,
      itemCount: currentRequest.cart?.cantidad_total ?? 0,
      products: currentRequest.products,
      removeItem,
      retry: () => setRetryVersion((version) => version + 1),
      updateQuantity,
    }),
    [
      addProduct,
      clear,
      completeCheckout,
      currentRequest,
      isMutating,
      removeItem,
      updateQuantity,
    ],
  );

  return <CartContext value={value}>{children}</CartContext>;
}
