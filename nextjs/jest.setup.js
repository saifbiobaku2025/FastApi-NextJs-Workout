import "@testing-library/jest-dom";

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
