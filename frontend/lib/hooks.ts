import { useDispatch, useSelector } from "react-redux";

import type { AppDispatch, RootState } from "./store";

// The same hooks as react-redux's, already told what our store looks like.
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
