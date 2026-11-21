import { configureStore } from "@reduxjs/toolkit";

import { api } from "./api";
import searchReducer from "./searchSlice";

// A function that makes a store, not a store itself. On the server a module-level store
// would be shared by every visitor's request; making one per app instance avoids that.
export const makeStore = () =>
  configureStore({
    reducer: { [api.reducerPath]: api.reducer, search: searchReducer },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
  });

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
