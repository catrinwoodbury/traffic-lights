//
//  ContentView.swift
//  Navigation System
//
//  Created by Woodbury Catrin on 3/13/24.
//
import SwiftUI

struct ContentView: View {
    @State private var showDetails = false
    var body: some View {
        VStack(alignment: .leading) {
                    Button("Start A Drive"){
                        showDetails.toggle()
                    }

                    if showDetails {
                        Text("here is the route!")
                            .font(.largeTitle)
                    }
                }
            }
        }
struct ContentView_Previews: PreviewProvider {

    static var previews: some View {

        ContentView()

    }
}
