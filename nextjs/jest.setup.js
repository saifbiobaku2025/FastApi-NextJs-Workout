import "@testing-library/jest-dom";

process.env.NEXT_PUBLIC_API_URL = "http://localhost:8000";

const mockPush = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

jest.mock("next/script", () => ({
  __esModule: true,
  default: (props) => <script {...props} />,
}));

beforeEach(() => {
  localStorage.clear();
  mockPush.mockClear();
});

global.mockPush = mockPush;
