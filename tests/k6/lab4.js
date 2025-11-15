import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.MAIN_API_URL || 'http://localhost:8000';
// const TARGET_ROUTE = __ENV.MAIN_API_ROUTE || '/api/v1/external/proxy';
const TARGET_ROUTE = __ENV.MAIN_API_ROUTE || '/api/v1/users/?limit=3000';
const SLEEP_BETWEEN_ITERS = Number(__ENV.K6_ITER_SLEEP || 0);
const REQUEST_TIMEOUT_MS = Number(__ENV.K6_HTTP_TIMEOUT || 190000);
const CASE_TAG = __ENV.K6_CASE || 'baseline';
const TEST_ID = __ENV.K6_TEST_ID || `lab4-local-${Date.now()}`;

export const options = {
  scenarios: {
    steady_load: {
      executor: __ENV.K6_EXECUTOR || 'constant-arrival-rate',
      rate: Number(__ENV.K6_RATE || 5),
      timeUnit: __ENV.K6_TIME_UNIT || '1s',
      duration: __ENV.K6_DURATION || '5m',
      preAllocatedVUs: Number(__ENV.K6_PRE_ALLOCATED_VUS || 20),
      maxVUs: Number(__ENV.K6_MAX_VUS || 200),
    },
  },
  tags: {
    test_suite: 'lab4',
    testid: TEST_ID,
  },
};

export default function () {
  const url = `${BASE_URL}${TARGET_ROUTE}`;
  const res = http.get(url, {
    timeout: REQUEST_TIMEOUT_MS,
    tags: {
      case: CASE_TAG,
    },
    headers: {
      'X-K6-TestCase': CASE_TAG,
    },
  });

  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });

  if (SLEEP_BETWEEN_ITERS > 0) {
    sleep(SLEEP_BETWEEN_ITERS);
  }
}
