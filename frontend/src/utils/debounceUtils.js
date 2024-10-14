// utils/debounceUtils.js
import { debounce } from 'lodash';

export const debouncedSearch = (callback, delay = 300) => {
  return debounce((value) => callback(value), delay);
};
