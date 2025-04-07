import SwiftUI

struct ContentView: View {
    // 1. State variable to store the text input
    @State private var userInput: String = "" // Start with an empty string

    var body: some View {
        VStack(spacing: 20) { // Arrange elements vertically
            Text("Please enter some text:")

            // 2. The TextField
            TextField("Type here...", text: $userInput) // "Type here..." is the placeholder
                .textFieldStyle(.roundedBorder) // Add a visual style
                .padding(.horizontal) // Add some horizontal space around it
                .autocapitalization(.none) // Optional: Prevent automatic capitalization
                .disableAutocorrection(true) // Optional: Turn off autocorrect

            // 3. Display the entered text (optional, just to show it works)
            Text("You entered: \(userInput)")

            // You can add a Button here to DO something with userInput
            Button("Submit") {
                // Action to perform when the button is tapped
                print("Submitting text: \(userInput)")
                // Call a function, send data, etc.
                // Clear the input field after submit?
                // userInput = ""
            }
            .buttonStyle(.borderedProminent)
            .disabled(userInput.isEmpty) // Disable button if input is empty

            Spacer() // Pushes content to the top
        }
        .padding() // Add padding around the whole VStack
    }
}

// This is for Xcode Previews
#Preview {
    ContentView()
}
