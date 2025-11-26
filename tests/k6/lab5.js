import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.MAIN_API_URL || 'http://localhost:8000';
const SCENARIO = __ENV.K6_SCENARIO || 'baseline';
const BROKER = __ENV.K6_BROKER || 'none';
const REQUEST_TIMEOUT_MS = Number(__ENV.K6_HTTP_TIMEOUT || 190000);
const CASE_TAG = __ENV.K6_CASE || `lab5-${SCENARIO}`;
const TEST_ID = __ENV.K6_TEST_ID || `lab5-${Date.now()}`;
const SLEEP_BETWEEN_ITERS = Number(__ENV.K6_ITER_SLEEP || 0);

function resolveRoute() {
  if (SCENARIO === 'baseline') {
    return { method: 'GET', url: `${BASE_URL}/api/v1/external/proxy` };
  }
  if (SCENARIO === 'async_upstream') {
    return {
      method: 'POST',
      url: `${BASE_URL}/api/v1/external/fetch/async-upstream?broker=${BROKER}`,
    };
  }
  if (SCENARIO === 'async_downstream') {
    return {
      method: 'POST',
      url: `${BASE_URL}/api/v1/external/fetch/async-downstream?broker=${BROKER}`,
    };
  }
  throw new Error(`Unknown scenario ${SCENARIO}`);
}

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
    test_suite: 'lab5',
    testid: TEST_ID,
    scenario: SCENARIO,
    broker: BROKER,
  },
};

export default function () {
  const target = resolveRoute();
  const requestParams = {
    timeout: REQUEST_TIMEOUT_MS,
    tags: {
      case: CASE_TAG,
      scenario: SCENARIO,
      broker: BROKER,
    },
    headers: {
      'X-K6-TestCase': CASE_TAG,
    },
  };

  let res;
  if (target.method === 'GET') {
    res = http.get(target.url, requestParams);
  } else {
    res = http.post(target.url, null, requestParams);
  }

  check(res, {
    'status is expected': (r) => {
      if (SCENARIO === 'async_upstream') {
        return r.status === 202;
      }
      return r.status >= 200 && r.status < 300;
    },
  });

  if (SLEEP_BETWEEN_ITERS > 0) {
    sleep(SLEEP_BETWEEN_ITERS);
  }
}
