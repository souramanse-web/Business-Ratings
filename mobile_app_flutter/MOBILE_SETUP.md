# Mobile MVP Setup (Flutter)

This guide helps you run the mobile MVP app in:
- Android (Windows)
- iOS (requires macOS)

Project path:
- `mobile_app_flutter/`

## 1) Install Flutter (Windows)

1. Download Flutter SDK:
   - https://docs.flutter.dev/get-started/install/windows/mobile
2. Extract to a folder, for example:
   - `C:\src\flutter`
3. Add Flutter to PATH:
   - Add `C:\src\flutter\bin` to your user/system `Path` environment variable.
4. Restart VS Code/terminal.

Verify:
```bash
flutter --version
flutter doctor
```

## 2) Install Android toolchain

1. Install Android Studio:
   - https://developer.android.com/studio
2. In Android Studio, install:
   - Android SDK
   - Android SDK Command-line Tools
   - Android Emulator
3. Create an Android Virtual Device (AVD):
   - Device Manager → Create device (e.g., Pixel)
4. Accept Android licenses:
```bash
flutter doctor --android-licenses
```

## 3) Run the mobile app (Android)

From project root:
```bash
cd mobile_app_flutter
flutter pub get
flutter run
```

If multiple devices are attached:
```bash
flutter devices
flutter run -d <device_id>
```

## 4) iOS build/run requirements

iOS builds require macOS with Xcode.

On macOS:
1. Install Xcode from App Store
2. Install CocoaPods:
```bash
sudo gem install cocoapods
```
3. Run:
```bash
cd mobile_app_flutter
flutter pub get
flutter run -d ios
```

## 5) Backend URL

The app currently points to production backend in:
- `lib/app/constants.dart`

Current value:
- `https://business-rating-app.onrender.com`

If you want to test local backend on emulator/device, update `baseUrl` accordingly.

## 6) Current MVP Screens

- Login
- Register
- Sector list
- Business list
- Business detail
- Submit rating
- Profile

## 7) Troubleshooting

### `flutter` command not found
- Ensure Flutter SDK `bin` folder is in PATH.
- Restart terminal/VS Code.

### Android emulator not detected
- Start emulator from Android Studio Device Manager first.
- Re-run `flutter devices`.

### API/network errors on login/data
- Confirm backend health:
  - `https://business-rating-app.onrender.com/healthz`
- Confirm CORS/network access if testing from custom environments.

## 8) Recommended next mobile steps

- Add persistent auth/session restoration on app restart
- Add error states and retry UI
- Add app icons/splash branding
- Prepare Android signing config and iOS bundle settings
- Set up TestFlight and Play Internal Testing
