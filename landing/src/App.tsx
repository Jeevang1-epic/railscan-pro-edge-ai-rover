import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Problem from './components/Problem'
import Solution from './components/Solution'
import Architecture from './components/Architecture'
import Demo from './components/Demo'
import Hardware from './components/Hardware'
import Validation from './components/Validation'
import CTA from './components/CTA'
import Footer from './components/Footer'

export default function App() {
  return (
    <div className="relative min-h-screen bg-rail-950 text-gray-200">
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <Solution />
        <Architecture />
        <Demo />
        <Hardware />
        <Validation />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}
